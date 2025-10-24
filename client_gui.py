import asyncio
import threading
import tkinter as tk
from tkinter import messagebox
import sys, traceback

from mcp import ClientSession, StdioServerParameters # type: ignore
from mcp.client.stdio import stdio_client # type: ignore

SERVER_CMD = sys.executable
SERVER_ARGS = ["server.py"]

def fmt(e: Exception) -> str:
    return "".join(traceback.format_exception_only(type(e), e)).strip()

class App:
    def __init__(self, root):
        self.root = root
        root.title("MCP Weather — Client")
        root.geometry("520x360")

        frame = tk.Frame(root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Ciudad:").grid(row=0, column=0, sticky="w")
        self.city_var = tk.StringVar(value="Montevideo")
        tk.Entry(frame, textvariable=self.city_var, width=28).grid(row=0, column=1, sticky="we")

        self.btn = tk.Button(frame, text="Consultar", command=self.on_click)
        self.btn.grid(row=1, column=0, columnspan=2, pady=8, sticky="we")

        self.out = tk.Text(frame, height=12, wrap="word")
        self.out.grid(row=2, column=0, columnspan=2, sticky="nsew")

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        self._append(f"(debug) Python: {sys.executable}")
        self._append("(debug) Preparado. Escribí una ciudad y tocá Consultar.")

    def on_click(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Falta ciudad", "Ingresá una ciudad")
            return

        self.btn.config(state="disabled")
        self.out.delete("1.0", tk.END)
        self._append("Consultando clima...\n")
        threading.Thread(target=self.run_mcp, args=(city,), daemon=True).start()

    def run_mcp(self, city: str):
        try:
            asyncio.run(self._async_call(city))
        except Exception as e:
            self._append(f"\nERROR hilo: {fmt(e)}")
        finally:
            self.root.after(0, lambda: self.btn.config(state="normal"))

    async def _async_call(self, city: str):
        params = StdioServerParameters(command=SERVER_CMD, args=SERVER_ARGS)
        self._append(f"(debug) Lanzando server: {SERVER_CMD} {SERVER_ARGS[0]}")
        try:
            async with stdio_client(params) as (read, write):
                self._append("(debug) Conectado por stdio ✔")
                async with ClientSession(read, write) as session:
                    self._append("(debug) Inicializando sesión…")
                    await session.initialize()
                    self._append("(debug) Llamando tool get_weather…")
                    res = await session.call_tool("get_weather", {"city": city})
                    shown = False
                    for c in res.content:
                        if getattr(c, "data", None) is not None:
                            self._append("Resultado JSON:")
                            self._append(str(c.data))
                            shown = True
                        elif getattr(c, "text", None):
                            self._append("Resultado texto:")
                            self._append(c.text)
                            shown = True
                    if not shown:
                        self._append("(Sin contenido)")
        except Exception as e:
            self._append("ERROR MCP: " + fmt(e))

    def _append(self, text: str):
        self.root.after(0, lambda: self.out.insert(tk.END, text + "\n"))

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
