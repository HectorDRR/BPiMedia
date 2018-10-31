var CanvasChart = function () {
    var ctx;
    var margin = { top: 40, left: 75, right: 30, bottom: 75 };
    var chartHeight, chartWidth, yMax, xMax, data;
    var maxYValue = 0;
	var minYValue = 0;
    var ratio = 0;
    var renderType = { lines: 'lines', points: 'points' };

    var render = function(canvasId, dataObj) {
        data = dataObj;
        getMaxDataYValue();
		getMinDataYValue();
        var canvas = document.getElementById(canvasId);
        chartHeight = canvas.getAttribute('height');
        chartWidth = canvas.getAttribute('width');
        xMax = chartWidth - (margin.left + margin.right);
        yMax = chartHeight - (margin.top + margin.bottom);
		//El ratio es lo que vale en el eje y cada punto representado y va relacionado a como representemos las xLabel, por lo que
		//tendremos que calcularlo teniendo en cuenta como hicimos el cálculo de éstas
        ratio = Math.round(yMax / (Math.trunc(maxYValue) - Math.trunc(minYValue) + 2));
        ctx = canvas.getContext("2d");
        renderChart();
    };

    var renderChart = function () {
        renderBackground();
        renderText();
        renderLinesAndLabels();

        //render data based upon type of renderType(s) that client supplies
        if (data.renderTypes == undefined || data.renderTypes == null) data.renderTypes = [renderType.lines];
        for (var i = 0; i < data.renderTypes.length; i++) {
            renderData(data.renderTypes[i]);
        }
    };

    var getMaxDataYValue = function () {
        for (var i = 0; i < data.dataPoints.length; i++) {
            if (data.dataPoints[i].y > maxYValue) maxYValue = data.dataPoints[i].y;
        }
    };

    var getMinDataYValue = function () {
		minYValue = maxYValue;
        for (var i = 0; i < data.dataPoints.length; i++) {
            if (data.dataPoints[i].y < minYValue) minYValue = data.dataPoints[i].y;
        }
    };

    var renderBackground = function() {
        var lingrad = ctx.createLinearGradient(margin.left, margin.top, xMax - margin.right, yMax);
        lingrad.addColorStop(0.0, '#D4D4D4');
        lingrad.addColorStop(0.2, '#fff');
        lingrad.addColorStop(0.8, '#fff');
        lingrad.addColorStop(1, '#D4D4D4');
        ctx.fillStyle = lingrad;
        ctx.fillRect(margin.left, margin.top, xMax, yMax - margin.top);
        ctx.fillStyle = 'black';
    };

    var renderText = function() {
        var labelFont = (data.labelFont != null) ? data.labelFont : '20pt Arial';
        ctx.font = labelFont;
        ctx.textAlign = "center";

        //Title
		//Estamos obteniendo la fecha de hoy, no la de los datos de la gráfica. Más adelante, este campo tendrá que provenir 
		//de los metadatos del HTML.
		if (data.fecha == undefined) {
			var fecha = new Date();
			//Los meses empiezan en 0 y los años en 1900
			fecha = fecha.getDate(fecha) + '/' + (Number(fecha.getMonth(fecha)) + 1) + '/' + (Number(fecha.getYear(fecha)) + 1900);
		} else var fecha = data.fecha;
        var txtSize = ctx.measureText(data.title + ' ' + fecha);
        ctx.fillText(data.title + ' ' + fecha, (chartWidth / 2), (margin.top / 2));

        //X-axis text
		//Añadimos el valor mínimo y máximo y los minutos conectada
		data.xLabel = data.xLabel + ', T. Min: ' + minYValue + ', T. Max: ' + maxYValue + ', Minutos conectada este mes: ' + data.conectada;
        txtSize = ctx.measureText(data.xLabel);
        ctx.fillText(data.xLabel, xMax - txtSize.width/2 - margin.left, yMax + (margin.bottom / 1.2));

        //Y-axis text
        ctx.save();
        ctx.rotate(-Math.PI / 2);
        ctx.font = labelFont;
        ctx.fillText(data.yLabel, (yMax / 2) * -1, margin.left / 4);
        ctx.restore();
    };

    var renderLinesAndLabels = function () {
        //Vertical guide lines
        //var yInc = yMax / data.dataPoints.length;
		var yInc = Math.round(yMax / (maxYValue - minYValue));
        var yPos = 0;
        var yLabelInc = (maxYValue * ratio) / data.dataPoints.length;
        var xInc = getXInc();
        var xPos = margin.left;
		//Si los datos a representar exceden el número de etiquetas en X que deseamos, lo rebajamos a un máximo de 24 (horas)
		if (data.maxXLabels == undefined) data.maxXLabels = 24;
		var cadax = (data.dataPoints.length > data.maxXLabels) ? Math.round(data.dataPoints.length / data.maxXLabels ): 1;
		var cont = 1;
		var conty = 1;
		//En caso de tener un rango fijo, como el de la temperatura, dibujamos las etiquetas de Y de manera independiente y dejando un valor
		//de más por arriba y por abajo
		if (data.maxYLabels == 'Fixed') {
			var caday = Math.trunc(maxYValue) - Math.trunc(minYValue) + 2;
			yPos = margin.top;
			yInc = Math.round(yMax/caday);
			//Empezamos en la esquina superior izquierda del gráfico, por lo que tenemos que ir restando
			for (var i = Math.trunc(maxYValue + 1); i > Math.trunc(minYValue) - 1; i--) {
				var txt = i;
				var txtSize = ctx.measureText(txt);
				ctx.fillText(txt, margin.left - ((txtSize.width >= 14) ? txtSize.width : 10) - 7, yPos + 4);
				//Draw horizontal lines
				drawLine(margin.left, yPos, xMax, yPos, '#E8E8E8');
				yPos += yInc;
			}	
		//Si los datos a representar exceden el número de etiquetas en Y que deseamos, lo rebajamos a un máximo de 24
		} else var caday = (data.dataPoints.length > data.maxYLabels) ? Math.round(data.dataPoints.length / 24 ): 1;
		console.log('Datos: ' + data.dataPoints.length + ' Ratio: ' + ratio + ' caday: ' + caday + ' yInc: ' + yInc + ' xMax: ' + xMax);
		ctx.font = (data.dataPointFont != null) ? data.dataPointFont : '10pt Calibri';
        for (var i = 0; i < data.dataPoints.length; i++) {
            yPos += (i == 0) ? margin.top : yInc;
			//Si el rango no es Fixed dibujamos las etiquetas Y partiendo de 0 en caso contrarioa ya han sido dibujadas antes del bucle
			if (data.maxYLabels != 'Fixed') {
				//y axis labels
				var txt = Math.round(maxYValue - ((i == 0) ? 0 : yPos / ratio));
				var txtSize = ctx.measureText(txt);
				if (conty == caday) {
					ctx.fillText(txt, margin.left - ((txtSize.width >= 14) ? txtSize.width : 10) - 7, yPos + 4);
					//Draw horizontal lines
					drawLine(margin.left, yPos, xMax, yPos, '#E8E8E8');
					conty = 0;
				}
				conty += 1;
			}
            //x axis labels
			//Dibujamos las etiquetas solo cadax para que no se pisen unas a otras
			if (cont == cadax || i == 0) {
				txt = data.dataPoints[i].x;
				txtSize = ctx.measureText(txt);
				ctx.fillText(txt, xPos, yMax + (margin.bottom / 3));
				cont = 0;
			}
			cont += 1;
			xPos += xInc;
        }

        //Vertical line
        drawLine(margin.left, margin.top, margin.left, yMax, 'black');

        //Horizontal Line
        drawLine(margin.left, yMax, xMax, yMax, 'black');
    };

    var renderData = function(type) {
        var xInc = getXInc();
        var prevX = 0, 
            prevY = 0;
		// Color del punto
		var colorao = 'Green';
		// Cada cuanto mostrar los puntos en caso de que excedan una cantidad razonable
		var cada = (data.dataPoints.length > data.maxXLabels) ? Math.round(data.dataPoints.length / 150 ): 1;
		var cont = 1;

        for (var i = 0; i < data.dataPoints.length; i++) {
            var pt = data.dataPoints[i];
			//Añadimos 1 para dejar un margen en el gráfico tanto por arriba como por abajo, 
			//al igual que hemos hecho con las etiquetas
			//Calculamos el desplazamiento en Y a partir del margen más el grado superior a la medida mayor x el ratio
            var ptY = margin.top + (Math.trunc(maxYValue) + 1 - pt.y) * ratio;
            if (ptY < margin.top) ptY = margin.top;
            var ptX = Math.round(i * xInc) + margin.left;
			if (i == 0) console.log(ptY, pt.y, ptX);

			//console.log(ptX, ptY, pt.y, margin.top);
            if (i > 0 && type == renderType.lines) {
                //Draw connecting lines
                drawLine(ptX, ptY, prevX, prevY, 'black', 2);
            }
			// Si en algún momento ha estado activo, el punto será rojo
			if (pt.z == 1) colorao = 'Red';
            if (cada == cont) {
				if (type == renderType.points) {
					var radgrad = ctx.createRadialGradient(ptX, ptY, 4, ptX - 5, ptY - 5, 0);
					radgrad.addColorStop(0, colorao);
					radgrad.addColorStop(0.9, 'White');
					ctx.beginPath();
					ctx.fillStyle = radgrad;
					//Render circle
					ctx.arc(ptX, ptY, 4, 0, 2 * Math.PI, false);
					ctx.fill();
					ctx.lineWidth = 1;
					ctx.strokeStyle = '#000';
					ctx.stroke();
					ctx.closePath();
				}
				cont = 0;
				colorao = 'Green';
			}
			cont += 1;
            prevX = ptX;
            prevY = ptY;
        }
		console.log(i, xInc);
    };

    var getXInc = function() {
        return (xMax / data.dataPoints.length) ;
    };

    var drawLine = function(startX, startY, endX, endY, strokeStyle, lineWidth) {
        if (strokeStyle != null) ctx.strokeStyle = strokeStyle;
        if (lineWidth != null) ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        ctx.closePath();
    };

    return {
        renderType: renderType,
        render: render
    };
} ();
