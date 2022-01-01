"""Запуск веб-сервера uvicorn
http://127.0.0.1:52005/docs
"""


import os
import uvicorn


if __name__ == '__main__':
    uvicorn.run(
        'server.app.main:app',
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "52005")),
        reload=True
    )
