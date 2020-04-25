setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
rem Macro para avisar a los aficionados a la HD de que he bajado nuevas pel�culas
rem Cambiamos el c�digo de p�gina al adecuado para soportar bien los acentos
chcp 1252
if defined debug set deb=rem
rem Se encarga de crear la falsa car�tula y Msheet para una serie de manera que Creaweb funcione correctamente y genere el enlace
for /f "delims=*" %%g in ('dir \\metal\series /ad /b') do (
if not exist "e:\trabajo\scaratulas\%%g.jpg" (
	echo >"e:\trabajo\scaratulas\%%g.jpg"
	echo >"e:\trabajo\sMsheets\%%g_sheet.jpg"
	echo Creada car�tula y msheet para %%g
	)
)
rem Nos bajamos la informaci�n de los trailers y generamos los .nfo necesarios
if not "%1"=="" (
	if not "%1"=="T" (
		set deb=rem
		goto lista
	) else goto trailer
)
set nohay=0
for %%g in (p:\pelis,p:\cortos,p:\Infantiles) do (
	pushd %%g
	rem Quitamos el atributo a los comentarios de las pelis para que no confundan la b�squeda de pel�culas nuevas
	attrib -a *.txt
	rem Eliminamos los comentarios de pelis que ya no est�n
	for %%f in (*.txt) do if not exist "%%~nf.mkv" del "%%f"
	dir /b /aa-h >nul:
	if errorlevel 1 set /a nohay+=1
	popd
)
pushd z:\
dir /b /s /aa-h *.avi *.mkv >nul:
if errorlevel 1 set /a nohay+=1
echo %nohay%
popd
if %nohay%==4 goto fin
:sigue
call :trailer
rem Para que no genere las listas completas de pel�culas. Tengo que estar atento a la etiqueta del disco porque cambia el nombre del fichero de pelis
set no=1
set nuevas=/aa-h
call e:\winutil\funciones.py ListaPelis 1
move /y e:\winutil\HD_Ultimas e:\winutil\HD_Anuncio
rem Hacemos una rutina especial para anunciar tambi�n las series, que no se est�n procesando correctamente
pushd z:\
for /d %%f in (*) do for /f "delims=*" %%g in ('dir /b /aa-h "%%f\*.avi" "%%f\*.mkv" "%%f\*.mp4"') do echo %%g:%%f:>>e:\winutil\HD_Anuncio
popd
call e:\winutil\funciones.py CreaWeb Anuncio 1
:lista
set no=1
rem Generamos las listas de pel�culas
call e:\winutil\funciones.py ListaPelis
rem Las agrupamos para crear un �ndice general
copy e:\winutil\Pelis_* "%temp%\Todas"
rem Generamos el �ndice de cada carpeta
for %%f in (Todas,Pelis,Cortos,Infantiles) do (
	copy e:\winutil\Pelis_%%f "%temp%\%%f"
	call e:\winutil\funciones.py CreaWeb %%f
	if not %%f==Todas (
		pushd p:\%%f
		move /y index.html %tmp%\index_%%f_old.html
		move "p:\pelis\%%f.html" index.html
		attrib -a index.html
		popd
	)
)
if not "%1"=="" goto fin
pushd p:\pelis
start Anuncio.html 
start index.html
"c:\Program Files (x86)\Notepad++\notepad++.exe" Anuncio.html index.html
pause
%deb% e:\winutil\gmailpelis.vbs
%deb% totrash Anuncio.html *.bak
for %%f in (p:\pelis,z:\,p:\cortos,p:\infantiles) do (
	cd /d %%f
	%deb% attrib -a * /D /S
)
:fin
set deb=
popd
goto :EOF
:trailer
rem Para usar en el trabajo solamente. Se encarga de bajarse la p�gina de �ltimas pel�culas para analizarla y extraer las que tengan trailers
rem para poder generar en el ordenador del curro el fichero .nfo con la informaci�n de la ruta del trailer de manera que al generar la p�gina
rem de pel�culas del trabajo, salga el enlace al trailer si �ste existe.
rem
rem Despu�s, nos bajamos las p�ginas y sobre la marcha extraemos la informaci�n necesaria
curl http://hrr.no-ip.info/Ultimas.html -o %tmp%\ulti.txt
curl http://hrr.no-ip.info/Todas.html -o %tmp%\toda.txt
copy %tmp%\ulti.txt + %tmp%\toda.txt %tmp%\Todas.html
for %%g in (p:\pelis,p:\cortos,p:\Infantiles) do (
	pushd %%g
	for /f "delims=*" %%f in ('dir /b /aa *.mkv *.mp4 *.avi') do (
		rem Si no existen los ficheros, los creamos
		if not exist "e:\trabajo\caratulas\%%~nf.jpg" (
			touch "e:\trabajo\caratulas\%%~nf.jpg"
			touch "e:\trabajo\Msheets\%%f_sheet.jpg"
		)
		funciones.py JTrailer "%%f" >%tmp%\tr.txt
		rem Lo siguiente mantiene el mismo valor de la iteraci�nanterior si el fichero tr.txt est� vac�o
		set /p tr=<%tmp%\tr.txt
		if not "!tr:~0,1!"=="N" (
			echo ^<movie^>^<trailer^>!tr!^</trailer^>^</movie^>>"%tmp%\NFO"
			echo !tr:~1,-1!
			if exist "e:\trabajo\msheets\%%f.tgmd" del "e:\trabajo\msheets\%%f.tgmd"
			"c:\Program Files\7-Zip\7z.exe" a -tzip "e:\trabajo\msheets\%%f.tgmd" "%tmp%\NFO"
			rem Creamos tambi�n el .nfo para usarlo en vez del .tgmd y asi no tener que estar descomprimiendo
			copy "%tmp%\NFO" "e:\trabajo\Msheets\%%~nf.nfo"
			del "%tmp%\NFO"
		)
		del %tmp%\tr.txt
	)
	popd
)
