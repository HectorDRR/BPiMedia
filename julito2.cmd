setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
rem Macro para avisar a los aficionados a la HD de que he bajado nuevas películas
rem Cambiamos el código de página al adecuado para soportar bien los acentos
chcp 1252
if defined debug set deb=rem
rem Se encarga de crear la falsa carátula y Msheet para una serie de manera que Creaweb funcione correctamente y genere el enlace
for /f "delims=*" %%g in ('dir \\metal\series /ad /b') do (
	if not exist "e:\trabajo\scaratulas\%%g.jpg" (
		echo >"e:\trabajo\scaratulas\%%g.jpg"
		echo >"e:\trabajo\sMsheets\%%g_sheet.jpg"
		echo Creada carátula y msheet para %%g
	)
)
pushd p:\pelis
rem Nos bajamos la información de los trailers y generamos los .nfo necesarios
if not "%1"=="" (
	if not "%1"=="T" (
		set deb=rem
		goto lista
	) else goto trailer
)
rem Quitamos el atributo a los comentarios de las pelis para que no confundan la búsqueda de películas nuevas
attrib -a *.txt
rem Eliminamos los comentarios de pelis que ya no estén
for %%f in (*.txt) do if not exist "%%~nf.mkv" del "%%f"
set nohay=0
dir /b /aa-h >nul:
if errorlevel 1 set /a nohay+=1
pushd p:\cortos
dir /b /aa-h >nul:
if errorlevel 1 set /a nohay+=1
echo %nohay%
popd
pushd z:\
dir /b /s /aa-h *.avi *.mkv >nul:
if errorlevel 1 set /a nohay+=1
echo %nohay%
popd
if %nohay%==3 goto fin
:sigue
call :trailer
rem Para que no genere las listas completas de películas. Tengo que estar atento a la etiqueta del disco porque cambia el nombre del fichero de pelis
set no=1
set nuevas=/aa-h
call e:\winutil\funciones.py ListaPelis 1
copy e:\winutil\HD_Ultimas %temp%\Anuncio
rem Hacemos una rutina especial para anunciar también las series, que no se están procesando correctamente
pushd z:\
for /d %%f in (*) do for /f "delims=*" %%g in ('dir /b /aa-h "%%f\*.avi" "%%f\*.mkv"') do echo %%g:%%f:>>%temp%\Anuncio
popd
rem Y otra para los cortos
pushd p:\Cortos
for /f "delims=*" %%g in ('dir /b /aa-h "*.avi" "*.mkv"') do echo %%g:Cortos:>>%temp%\Anuncio
popd
call e:\winutil\funciones.py CreaWeb Anuncio 1
:lista
set no=1
call e:\winutil\funciones.py ListaPelis
copy e:\winutil\Pelis_Pelis "%temp%\Pelis"
call e:\winutil\funciones.py CreaWeb "Pelis"
move /y index.html j:\temp\index_old.html
ren "p:\pelis\Pelis.html" index.html
attrib -a index.html
if not "%1"=="" goto fin
start Anuncio.html 
start index.html
"c:\Program Files (x86)\Notepad++\notepad++.exe" Anuncio.html index.html
pause
%deb% e:\winutil\gmailpelis.vbs
%deb% totrash Anuncio.html *.bak
%deb% attrib -a * /D /S
pushd z:\
%deb% attrib -a * /D /S
popd
pushd p:\cortos
%deb% attrib -a *
popd
:fin
set deb=
popd
goto :EOF
:trailer
rem Para usar en el trabajo solamente. Se encarga de bajarse la página de últimas películas para analizarla y extraer las que tengan trailers
rem para poder generar en el ordenador del curro el fichero .nfo con la información de la ruta del trailer de manera que al generar la página
rem de películas del trabajo, salga el enlace al trailer si éste existe.
rem
rem Después, nos bajamos las páginas y sobre la marcha extraemos la información necesaria
curl http://hrr.no-ip.info/Ultimas.html -o %tmp%\ulti.txt
curl http://hrr.no-ip.info/Todas.html -o %tmp%\toda.txt
copy %tmp%\ulti.txt + %tmp%\toda.txt %tmp%\Todas.html
for /f "delims=*" %%f in ('dir /b /aa *.mkv') do (
	rem Si no existen los ficheros, los creamos
	if not exist "e:\trabajo\caratulas\%%~nf.jpg" (
		touch "e:\trabajo\caratulas\%%~nf.jpg"
		touch "e:\trabajo\Msheets\%%f_sheet.jpg"
	)
	funciones.py JTrailer "%%f" >%tmp%\tr.txt
	rem Lo siguiente mantiene el mismo valor de la iteraciónanterior si el fichero tr.txt está vacío
	set /p tr=<%tmp%\tr.txt
	if not "!tr:~0,1!"=="N" (
		echo ^<movie^>^<trailer^>!tr:~1,-1!^</trailer^>^</movie^>>"%tmp%\NFO"
		echo !tr:~1,-1!
		if exist "e:\trabajo\msheets\%%f.tgmd" del "e:\trabajo\msheets\%%f.tgmd"
		"c:\Program Files\7-Zip\7z.exe" a -tzip "e:\trabajo\msheets\%%f.tgmd" "%tmp%\NFO"
		del "%tmp%\NFO"	
	)
	del %tmp%\tr.txt
)
