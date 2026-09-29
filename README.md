# LocalCodeEditor

A mobile-friendly editor starter with a browser-based offline mode and an optional local Termux API.

## Browser mode
Open `index.html` from a local web server. Browser mode stores projects in localStorage and supports import/export and HTML preview.

## Termux mode
Install Python and the optional language runtimes, then start the local API:

```sh
bash termux-setup.sh
python server.py
```

Open **http://127.0.0.1:8765** in the same device browser and tap **Connect Termux**. The Termux file selector can refresh and open existing files from the project folder. **Save to Termux** writes the active file back to its original relative path (or its filename for a browser-only file).

The Run panel supports Python, Node.js, and PHP when installed. Choose a runtime and tap **Run** to execute the editor contents.

## Security and limitations
- The API binds only to `127.0.0.1`; do not expose it to a public network.
- Running code executes with the same permissions as Termux and can access files available to that account. Run only code you trust.
- Each run is limited to 10 seconds; output is truncated.
- The current UI is a starter, not a full PTY terminal or advanced IDE. Browser storage and Termux project files are separate. MariaDB integration is not included.
