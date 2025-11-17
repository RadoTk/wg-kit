
## Creating a Django App in the `app/` Directory

To create a new Django application inside the `app/` folder, follow these steps:

1. Ensure the destination directory exists.  
   If it doesn’t, create it first:

   ```bash
   mkdir app/contact
   ```

2. Run the `startapp` command, pointing to the nested path:

   ```bash
   python ./manage.py startapp contact app/contact
   ```

> **Note:** Django will place the new app’s files inside `app/contact/` only if the directory already exists; otherwise it raises a `CommandError`.
