
# ClamAV Tkinter - Escáner de archivos y directorios

ClamAV GUI es una interfaz gráfica de usuario (GUI) diseñada para facilitar el uso de ClamAV, un software antivirus de código abierto. Esta aplicación está inspirada en proyectos como ClamWin y ClamTk, y ofrece una experiencia más accesible y visual para los usuarios que desean realizar escaneos antivirus en sus sistemas de forma rápida y sencilla.

## Características

-   **Escanear archivos o directorios:** Selecciona un archivo o carpeta para escanear en busca de virus.
    
-   **Historial de escaneos:** Guarda los resultados de cada escaneo y permite verlos posteriormente.
    
-   **Actualización de la base de datos:** Actualiza la base de datos de virus usando `freshclam`.
    
-   **Detección de versión de ClamAV:** Verifica la versión instalada y la fecha de la última actualización.
    

## Requisitos

-   Python 3.7+
    
-   ClamAV instalado (`clamscan`, `freshclam`)
    
-   Tkinter (incluido en la instalación estándar de Python)
    

En Ubuntu/Debian, puedes instalar ClamAV con:

```
sudo apt update
sudo apt install clamav clamav-daemon
```

## Instalación

1.  Clona este repositorio:
    

```
git clone https://github.com/tu-usuario/clamav-tkinter.git
cd clamav-tkinter
```

2.  Instala las dependencias (si es necesario):
    
`tkinter`: Viene con Python en Windows y macOS. En Linux, si falta, puedes instalarlo con:
```
sudo apt install python3-tk
```

## Imagenes
![Image](https://github.com/user-attachments/assets/14e15cd1-5287-44f7-a1f0-b1a20888f334)

  

![Image](https://github.com/user-attachments/assets/dbd546d2-a4bc-4839-add4-f313425ff0b7)

  

![Image](https://github.com/user-attachments/assets/1c0215bc-d4f9-4dc4-8dc4-a5014a95cacc)

Crédito del icono: [diamonjohn en Openclipart](https://openclipart.org/artist/diamonjohn)