@echo off
:: Create the directory
mkdir C:\AutoAccepter

:: Change to the new directory
cd C:\AutoAccepter

:: Download the executable file
curl -L -o AutoAccepterV1.exe https://github.com/fpsheaven/AutoAccepter/releases/download/v1/AutoAccepterV1.exe

:: Download the image
curl -L -o accept.png https://github.com/fpsheaven/AutoAccepter/raw/main/accept.png
:: Downloading the Library
cls
echo I am downloading a library called Tesseract for the app to work. Just press yes to all.
timeout /t 5
curl -L -o tesseract-ocr-w64-setup-5.5.0.20241111.exe https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe
tesseract-ocr-w64-setup-5.5.0.20241111.exe /VERYSILENT /SUPPRESSMSGBOXES /D=C:\Program Files\Tesseract-OCR


:: Launch the executable
AutoAccepterV1.exe
