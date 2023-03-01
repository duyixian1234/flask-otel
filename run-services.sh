concurrently --prefix "{name}-{pid}"\
    -c "bgBlue.bold,bgMagenta.bold,bgGreen.bold,bgYellow.bold,bgGray.bold"\
    --names "main,upstream,service1,service2,log"\
    "flask --app=main:app run --reload"\
    "uvicorn upstream:app --port 5001 --reload"\
    "uvicorn service1:app --port 5002 --reload"\
    "uvicorn service2:app --port 5003 --reload"\
    "uvicorn log:app --port 5004 --reload"\
    