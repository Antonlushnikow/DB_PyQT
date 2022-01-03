Server app
==========

Сервер мессенджера. Запускается с графической оболочкой

Пример запуска:

``python main.py``


main.py
~~~~~~~~~~~~

Запускаемый модуль

.. autoclass:: server.main.Server
    :members:


models.py
~~~~~~~~~

Описание базы данных

.. autoclass:: server.app.models.User
    :members:

.. autoclass:: server.app.models.UserContact
    :members:

.. autoclass:: server.app.models.UserHistory
    :members:


server_gui.py
~~~~~~~~~~~~~

Графический интерфейс сервера. Обработчик нажатия кнопок


.. autoclass:: server.app.server_gui.ServerGUI
    :members:

