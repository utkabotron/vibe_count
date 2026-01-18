#!/usr/bin/env python3
"""
Cleanup Timeweb server
"""
import paramiko

HOST = "188.225.46.190"
USERNAME = "root"
PASSWORD = "b7AAm^YH*@gUjp"

def main():
    print("="*60)
    print("  Очистка сервера Timeweb")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Remove cron job
        print("1. Удаление cron задачи...")
        stdin, stdout, stderr = ssh.exec_command("crontab -r 2>/dev/null || echo 'No crontab'")
        result = stdout.read().decode().strip()
        stdout.channel.recv_exit_status()
        print(f"   ✓ Cron очищен")

        # 2. Stop any running processes
        print("\n2. Остановка процессов...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'vibe_count' || true")
        stdout.channel.recv_exit_status()
        print("   ✓ Процессы остановлены")

        # 3. Remove project directory
        print("\n3. Удаление директории проекта...")
        stdin, stdout, stderr = ssh.exec_command("rm -rf /root/vibe_count")
        stdout.channel.recv_exit_status()
        print("   ✓ /root/vibe_count удалена")

        # 4. Verify cleanup
        print("\n4. Проверка очистки...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /root/vibe_count 2>&1")
        result = stdout.read().decode()

        if "No such file or directory" in result or "cannot access" in result:
            print("   ✓ Проект полностью удален")
        else:
            print("   ⚠️  Остались файлы:")
            print(result)

        stdin, stdout, stderr = ssh.exec_command("crontab -l 2>&1")
        cron_result = stdout.read().decode()
        if "no crontab" in cron_result.lower():
            print("   ✓ Cron пуст")
        else:
            print("   ⚠️  Cron содержит:")
            print(cron_result)

        print("\n" + "="*60)
        print("  ✓ СЕРВЕР ОЧИЩЕН")
        print("="*60)
        print("\nТеперь можно развернуть на новом сервере")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
