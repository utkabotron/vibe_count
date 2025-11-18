"""
REST API для обработки документов
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

# Импортируем наш обработчик
from .main import handler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания статуса обработки
processing_status = {
    "is_processing": False,
    "last_run": None,
    "last_result": None,
    "total_processed": 0,
    "auto_mode": True,  # Автоматическая обработка включена по умолчанию
    "check_interval": 30  # Проверять каждые 30 секунд
}

# Фоновая задача для автоматической обработки
async def auto_process_loop():
    """Фоновая задача, которая периодически проверяет папку и обрабатывает файлы"""
    logger.info("Запуск автоматической обработки файлов")

    while True:
        try:
            # Проверяем, включен ли автоматический режим
            if not processing_status["auto_mode"]:
                await asyncio.sleep(processing_status["check_interval"])
                continue

            # Если уже идёт обработка, пропускаем
            if processing_status["is_processing"]:
                await asyncio.sleep(processing_status["check_interval"])
                continue

            # Запускаем обработку
            logger.debug(f"Проверка папки /Входящие")
            result = handler()

            # Если файл был обработан
            if result.get("statusCode") == 200:
                processing_status["is_processing"] = False
                processing_status["last_run"] = datetime.now().isoformat()
                processing_status["last_result"] = result
                processing_status["total_processed"] += 1
                logger.info(f"Автоматически обработан файл: {result.get('body')}")
            elif result.get("statusCode") == 400:
                # Файл с ошибками валидации
                processing_status["is_processing"] = False
                processing_status["last_run"] = datetime.now().isoformat()
                processing_status["last_result"] = result
                logger.warning(f"Файл с ошибками: {result.get('body')}")
            else:
                # Нет файлов для обработки - это нормально
                processing_status["is_processing"] = False

        except Exception as e:
            processing_status["is_processing"] = False
            logger.error(f"Ошибка в автоматической обработке: {e}", exc_info=True)

        # Ждём до следующей проверки
        await asyncio.sleep(processing_status["check_interval"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск - создаём фоновую задачу
    task = asyncio.create_task(auto_process_loop())
    logger.info("Фоновая задача автообработки запущена")
    yield
    # Остановка - отменяем задачу
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Фоновая задача автообработки остановлена")


app = FastAPI(
    title="Invoice AI Pipeline API",
    description="API для автоматической обработки бухгалтерских документов",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Invoice AI Pipeline API",
        "version": "2.0.0",
        "description": "Автоматическая обработка файлов из /vibe/Входящие",
        "auto_mode": processing_status["auto_mode"],
        "check_interval": f"{processing_status['check_interval']} секунд",
        "endpoints": {
            "GET /": "Информация об API",
            "GET /health": "Healthcheck",
            "GET /status": "Статус системы и автообработки",
            "POST /process": "Обработать следующий файл вручную",
            "POST /process-sync": "Обработать файл синхронно",
            "POST /auto/enable": "Включить автоматическую обработку",
            "POST /auto/disable": "Выключить автоматическую обработку",
            "POST /auto/interval/{seconds}": "Установить интервал проверки"
        }
    }


@app.get("/health")
async def health():
    """Healthcheck эндпоинт"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """Получить статус системы"""
    return {
        "is_processing": processing_status["is_processing"],
        "last_run": processing_status["last_run"],
        "last_result": processing_status["last_result"],
        "total_processed": processing_status["total_processed"],
        "auto_mode": processing_status["auto_mode"],
        "check_interval": processing_status["check_interval"]
    }


@app.post("/auto/enable")
async def enable_auto_mode():
    """Включить автоматическую обработку"""
    processing_status["auto_mode"] = True
    logger.info("Автоматическая обработка включена")
    return {"message": "Автоматическая обработка включена"}


@app.post("/auto/disable")
async def disable_auto_mode():
    """Выключить автоматическую обработку"""
    processing_status["auto_mode"] = False
    logger.info("Автоматическая обработка выключена")
    return {"message": "Автоматическая обработка выключена"}


@app.post("/auto/interval/{seconds}")
async def set_check_interval(seconds: int):
    """Установить интервал проверки папки (в секундах)"""
    if seconds < 5:
        raise HTTPException(status_code=400, detail="Минимальный интервал: 5 секунд")
    if seconds > 3600:
        raise HTTPException(status_code=400, detail="Максимальный интервал: 3600 секунд (1 час)")

    processing_status["check_interval"] = seconds
    logger.info(f"Интервал проверки изменён на {seconds} секунд")
    return {"message": f"Интервал проверки установлен: {seconds} секунд"}


async def process_document():
    """Фоновая задача для обработки документа"""
    global processing_status

    try:
        processing_status["is_processing"] = True
        processing_status["last_run"] = datetime.now().isoformat()

        logger.info("Запуск обработки через API")
        result = handler()

        processing_status["last_result"] = result
        processing_status["is_processing"] = False

        if result.get("statusCode") == 200:
            processing_status["total_processed"] += 1
            logger.info(f"Документ успешно обработан: {result.get('body')}")
        else:
            logger.warning(f"Обработка завершена с предупреждением: {result.get('body')}")

    except Exception as e:
        processing_status["is_processing"] = False
        processing_status["last_result"] = {
            "statusCode": 500,
            "body": f"Ошибка: {str(e)}"
        }
        logger.error(f"Ошибка при обработке: {e}", exc_info=True)


@app.post("/process")
async def process_next_file(background_tasks: BackgroundTasks):
    """
    Обработать следующий файл из папки /Входящие

    Запускает обработку в фоновом режиме и сразу возвращает ответ
    """
    if processing_status["is_processing"]:
        raise HTTPException(
            status_code=409,
            detail="Обработка уже выполняется. Подождите завершения."
        )

    # Запускаем обработку в фоне
    background_tasks.add_task(process_document)

    return JSONResponse(
        status_code=202,
        content={
            "message": "Обработка запущена",
            "status_url": "/status"
        }
    )


@app.post("/process-sync")
async def process_sync():
    """
    Синхронная обработка (ждет завершения)

    Используйте для тестирования или когда нужен немедленный результат
    """
    if processing_status["is_processing"]:
        raise HTTPException(
            status_code=409,
            detail="Обработка уже выполняется. Подождите завершения."
        )

    try:
        processing_status["is_processing"] = True
        processing_status["last_run"] = datetime.now().isoformat()

        logger.info("Запуск синхронной обработки через API")
        result = handler()

        processing_status["last_result"] = result
        processing_status["is_processing"] = False

        if result.get("statusCode") == 200:
            processing_status["total_processed"] += 1

        return result

    except Exception as e:
        processing_status["is_processing"] = False
        logger.error(f"Ошибка при обработке: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
