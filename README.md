# LocalCodeEditor

A lightweight, offline-first, mobile-friendly code editor starter designed to run locally in a browser or from Termux.

## Features

- Installable offline PWA shell
- File list with create, rename, and delete
- Text editor with local browser storage
- HTML preview for the active file
- Import and export text files

## Run

From this directory in Termux:

```sh
python -m http.server 8080
```

Open `http://localhost:8080` in your browser. Service workers require localhost or HTTPS.

## Current limitations

This starter does not yet include a native terminal, language runtime execution, filesystem access beyond browser storage/import-export, or MariaDB integration. Browser storage is separate from Termux files.