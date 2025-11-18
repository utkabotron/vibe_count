"""
REST API для обработки документов
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

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

app = FastAPI(
    title="Invoice AI Pipeline API",
    description="API для автоматической обработки бухгалтерских документов",
    version="1.0.0"
)

# Глобальная переменная для отслеживания статуса обработки
processing_status = {
    "is_processing": False,
    "last_run": None,
    "last_result": None,
    "total_processed": 0
}


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Invoice AI Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Обработать следующий файл из /Входящие",
            "GET /status": "Статус системы и последнего запуска",
            "GET /health": "Healthcheck"
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
        "total_processed": processing_status["total_processed"]
    }


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
