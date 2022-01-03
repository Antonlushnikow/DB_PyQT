Client app
==========

Сервер мессенджера. Запускается с графической оболочкой

Пример запуска:

``python main.py``


main.py
~~~~~~~~~~~~

Запускаемый модуль

.. autoclass:: client.main.Client
    :members:


models.py
~~~~~~~~~

Описание базы данных

.. autoclass:: client.app.models.UserContact
    :members:

.. autoclass:: client.app.models.MessageHistory
    :members:




client_gui.py
~~~~~~~~~~~~~

Графический интерфейс клиента


.. autoclass:: client.app.client_gui.StartWindow
    :members:


.. autoclass:: client.app.client_gui.MainWindow
    :members:


.. autoclass:: client.app.client_gui.RegisterWindow
    :members:


.. autoclass:: client.app.client_gui.UsersWindow
    :members:


.. autoclass:: client.app.client_gui.ChatWindow
    :members:

