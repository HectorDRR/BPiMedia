# Se encarga de borrar los ficheros más viejos de x días +x partiendo delactual, ejemplo 
# si estamos a día 23 y le decimos +1 borrará los del día 22 y anterior
find . -mtime $1 -exec echo {} +
read a
find . -mtime $1 -exec rm {} +
