#!/bin/bash
export DISPLAY=:1.0
export XAUTHORITY=/home/ubuntu/.Xauthority

# Проверяем, запущен ли уже процесс neonirony_bot.py
if pgrep -f "python3 ./neonirony_bot.py" > /dev/null; then
   nohup  echo "neonirony_bot.py уже запущен"
else
    # Если не запущен, запускаем
  nohup  python3 ./neonirony_bot.py &
fi

# Дополнительные команды скрипта

# Пример: Проверка и запуск другого процесса
# Аналогично для go_post.py
if pgrep -f "python3 ./go_post.py" > /dev/null; then
   nohup echo "go_post.py уже запущен"
else
   nohup sh -c 'DISPLAY=:1.0 konsole --fullscreen -e python3 ./go_post.py' &
fi

# Дополнительные команды могут быть здесь

