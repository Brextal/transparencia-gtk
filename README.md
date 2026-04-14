# Transparencia GTK

Aplicación para **controlar la transparencia de ventanas en Hyprland** mediante una interfaz gráfica sencilla construida en **Python + GTK**.

##  Características
- **Control de transparencia** de ventanas en tiempo real.  
- Interfaz gráfica amigable con **GTK**.  
- Configuración rápida y ligera.  
- Código abierto y extensible para personalización.  

##  Estructura del proyecto
- `ventana.py`: Lógica principal de la ventana GTK.  
- `test_ventana.py`: Script de prueba para la interfaz.  
- `transparencia/`: Módulo encargado de aplicar los cambios de transparencia.  
- `estilo.css`: Estilos visuales de la aplicación.  

## ⚙️ Requisitos
- **Hyprland** instalado y funcionando.  
- **Python 3.10+**  
- Librerías necesarias:  
  ```bash
  pip install pygtk
  ```
## 🚀 Instalación y uso
Clona el repositorio:

```bash
git clone https://github.com/Brextal/transparencia-gtk.git
cd transparencia-gtk
```

Ejecuta la aplicación:
```bash
python3 ventana.py
```
Ajusta la transparencia de tus ventanas directamente desde la interfaz.

![Interfaz gráfica](2026-04-14-164048.png)

## Contribuciones
Las contribuciones son bienvenidas.

- Haz un **fork** del proyecto.  
- Crea una rama con tu mejora:  

```bash
git checkout -b mi-mejora
```
- Envía un pull request.

## 📜 Licencia
Este proyecto está bajo la licencia MIT, lo que permite su uso, modificación y distribución libremente.



