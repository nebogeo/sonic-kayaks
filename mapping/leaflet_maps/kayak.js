/////////////
//Basemaps//
////////////
var hl = L.hotline;

var viridis_palette =  {
    0.0: '#440154FF',
    0.05: '#481567FF',
    0.1: '#482677FF',
    0.15: '#453781FF',
    0.2: '#404788FF',
    0.25: '#39568CFF',
    0.3: '#33638DFF',
    0.35: '#2D708EFF',
    0.4: '#287D8EFF',
    0.45: '#238A8DFF',
    0.5: '#1F968BFF',
    0.55: '#20A387FF',
    0.6: '#29AF7FFF',
    0.65: '#3CBB75FF',
    0.7: '#55C667FF',
    0.75: '#73D055FF',
    0.8: '#95D840FF',
    0.85: '#B8DE29FF',
    0.9: '#DCE319FF',
    1: '#FDE725FF',
};

function palette_lookup(v,min,max) {
    var t=(v-min)/(max-min);
    if (t<0) { return viridis_palette[0]; }
    if (t>=1) { return viridis_palette[1]; }

    var keys = Object.keys(viridis_palette).sort();
    
    for (var i=0; i<keys.length; i++) {
	var k = keys[i];
	if (k>t) {
	    return viridis_palette[k];
	}
    }
    return '#000';
}

$.ajaxSetup({
    scriptCharset: "utf-8",
    contentType: "application/json; charset=utf-8"
});

$( document ).ready(function() {
    var map = L.map('map',{
	center: [50.160626, -5.073639],
	zoom: 15,
	zoomControl: false
    });

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg',{
	maxZoom: 20,
	subdomains:['mt0','mt1','mt2','mt3'],
	attribution: "Sources: Esri, DigitalGlobe, GeoEye, i-cubed, USDA FSA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community"

    }).addTo(map);

/*    L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
	maxZoom: 20,
	subdomains:['mt0','mt1','mt2','mt3']
    }).addTo(map);
*/
    trips=new Set()
    sensor_layers=[]
    hex_layer=new L.GeoJSON();
    map.addLayer(hex_layer);
    current_sensor="temp"
    current_viz="points"
    ranges = [[15,20],
	      [400,700],
	      [0,5],
	      [0,1]]
	    
////////////////////////////////////////////////////////////////
    
    function clear_hex(el) {
	hex_layer.clearLayers();
    }

    function data_name_from_id(id) {
	if (id.includes("temp")) return "mean_temp";
	if (id.includes("turbidity")) return "mean_turbid";
	if (id.includes("pm1_std")) return "mean_pm";
	if (id.includes("pm25_std")) return "mean_pm";
	if (id.includes("pm10_std")) return "mean_pm";
	if (id.includes("p_rms_std")) return "mean_p_rms_db";
	if (id.includes("tol_cf_125hz")) return "mean_tol_cf_125Hz";
	if (id.includes("small_boats")) return "mean_small_boats";
	if (id.includes("big_boats")) return "mean_big_boats";
	if (id.includes("large_ships")) return "mean_large_ships";
    }

    function title_from_id(id) {
	if (id.includes("temp")) return "Mean Temperature (°C)";
	if (id.includes("turbidity")) return "Mean Turbididy (Light level in volts across LDR sensor)";
	if (id.includes("pm1_std")) return "Mean Particulate Matter (1.0μg/m<sup>3</sup>)";
	if (id.includes("pm25_std")) return "Mean Particulate Matter (2.5μg/m<sup>3</sup>)";
	if (id.includes("pm10_std")) return "Mean Particulate Matter (10.0μg/<sup>m3</sup>)";
	if (id.includes("p_rms_std")) return "Broadband Mean SPL<sub>rms</sub> dB re 1 μPa";
	if (id.includes("tol_cf_125hz")) return "125 Hz Mean TOL dB re 1 μPa";
	if (id.includes("small_boats")) return "Small Boats Mean SPL<sub>rms</sub> dB re 1 μPa";
	if (id.includes("big_boats")) return "Big Boats Mean SPL<sub>rms</sub> dB re 1 μPa";
	if (id.includes("large_ships")) return "Large Ships Mean SPL<sub>rms</sub> dB re 1 μPa";
    }
    

    function hex_style(id,feature,min,max) {
	var d=feature.properties[data_name_from_id(id)];
	if (d==null) {
	    return {
		fillOpacity: 0.0,
		weight: 1.0,
		color: "#000000",
	    };
	} else {
	    var v=palette_lookup(d,min,max);
	    return {
		color: "#000000",
		weight: 1.0,
		fillColor: v,
		fillOpacity: 1.0
	    };
	}
    }
    
    function draw_hex(el) {
	hex_layer.clearLayers();
	
	$.getJSON("geojson/"+el.srcElement.id+".geojson", function (data) {
	    var min=Number.MAX_VALUE;
	    var max=0;
	    var dataname = data_name_from_id(el.srcElement.id);
	    data.features.forEach(function(feature) {
		var v = feature.properties[dataname];
		if (v!=null) {
		    if (v<min) min=v;
		    if (v>max) max=v;
		}
	    });	    

	    override_scale("<div style='width:10em; margin-bottom:1em;'><b>"+title_from_id(el.srcElement.id)+"</b></div>",min,max);
	    
	    L.geoJSON(data, {
		style: function(feature) {
		    return hex_style(el.srcElement.id,feature,min,max);
		}
	    }).addTo(hex_layer);
	});
    }

////////////////////////////////////////////////////////////////

    function update_scale() {
	_update_scale(document.getElementById("scale"));
    }
    
    function _update_scale(div) {
	var grades = [];
	var range=1;
	var min=ranges[range][0];
	var max=ranges[range][1];
        for (i=0; i<20; i++) {
	    grades.push(min+((max-min)*i/20));
	}
	
	div.innerHTML = "<div><h3>Turbidity</h3>Light level in V across LDR</div><br/>";
        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = grades.length-1; i>=0; i--) {
            div.innerHTML +=
		'<div style="overflow:hidden;"><i style="background:' + palette_lookup(grades[i],ranges[range][0],ranges[range][1]) + '"> </i><i> ' +
                ((grades[i]/1024)*3.3).toFixed(3) + 'v</i></div>';
        }
    }

    function override_scale(title,min,max) {
	var div=document.getElementById("scale")
	var grades = [];
	var range=1;
        for (i=0; i<20; i++) {
	    grades.push(min+((max-min)*i/20));
	}
	
	div.innerHTML = title;
        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = grades.length-1; i>=0; i--) {
            div.innerHTML +=
		'<div style="overflow:hidden;"><i style="background:' + palette_lookup(grades[i],min,max) + '"> </i><i> ' +
                grades[i].toFixed(3) + '</i></div>';
        }
    }
    
//////////////////////////////////////////////////////////////////
    
    function draw_trip(el) {
	el=el.srcElement
	if (el.checked) {
	    trips.add(el.id)
	} else {
	    trips.delete(el.id)
	}
	inner_draw_sensor(current_sensor);
    }
    
    function draw_viz(el) {
	current_viz=el.srcElement.id;
	inner_draw_sensor(current_sensor);
    }

    function draw_sensor(el) {
	inner_draw_sensor(el.srcElement.id);
    }

    function inner_draw_sensor(id) {
	sensor="";
	min=0;
	max=0;
	current_sensor=id;

	update_scale();
	
	switch (id) {
	case "temp": min=ranges[0][0]; max=ranges[0][1]; break;
	case "turbid_raw": min=ranges[1][0]; max=ranges[1][1]; break;
	default: min=ranges[2][0]; max=ranges[2][1]; break;
	}
	
	sensor_layers.forEach(function(layer) {
	    map.removeLayer(layer)
	});
	sensor_layers=[]
	
	trips.forEach(function(trip) {
	    fn = ""
	    switch(trip) {
	    case "t1": fn="20-07-23-sk1-dave-penryn-test-"; break;
	    case "t2": fn="20-07-29-sk1-jo-"; break;
	    case "t3": fn="20-07-29-sk2-james-"; break;
	    case "t4": fn="20-07-29-sk3-amber-"; break;
	    case "t5": fn="20-08-04-sk1-dave-penryn-loop-"; break;
	    case "t6": fn="20-08-07-sk1-amber-helford-"; break;
	    }

	    switch (current_viz) {
	    case "heatline": load_data_heatline("geojson/"+fn+id+".geojson",min,max); break;
	    default: load_data_points("geojson/"+fn+id+".geojson",min,max); break;
	    }
	});
    }

    function load_data_heatline(geojson,min,max) {
	//Loading a GeoJSON file (using jQuery's $.getJSON)
	$.getJSON(geojson, function (data) {

	    myarray = [];

            //grab the xyz data from the array
            data.features.forEach(function(feature){
		point_array = []
		point_array.push(feature.geometry.coordinates[1])
		point_array.push(feature.geometry.coordinates[0])
		point_array.push(feature.properties.data)
		myarray.push(point_array)
            });

	    //using an array with xyz, plot the hotline
	    var hotlineLayer = hl(myarray, {
		min: min, max: max,
		palette: viridis_palette,
		weight: 4.5,
      		outlineColor: '#8c8c8c',
      		outlineWidth: 0
      	    });

	    hotlineLayer.addTo(map);
	    hotlineLayer.bringToFront();
	    hex_layer.bringToBack();
	    sensor_layers.push(hotlineLayer);
	    
	});
    }

    function load_data_points(geojson,min,max) {
	//Loading a GeoJSON file (using jQuery's $.getJSON)
	$.getJSON(geojson, function (data) {
	    myarray = [];
	    var points_layer = new L.GeoJSON();
            //grab the xyz data from the array

	    data.features.forEach(function(feature){
		var col = palette_lookup(feature.properties.data,min,max);
		
		L.circle([feature.geometry.coordinates[1],
			  feature.geometry.coordinates[0]],
			 {
			     color: col,
			     fillColor: col,
			     fillOpacity: 1.0,
			     radius: 0.5
			 }).addTo(points_layer);		
            });
	    points_layer.addTo(map);
	    sensor_layers.push(points_layer);
	});
    }
    
   
    document.getElementById("temp").addEventListener("click",draw_sensor);
    document.getElementById("turbid_raw").addEventListener("click",draw_sensor);
    document.getElementById("pm_std_2_5").addEventListener("click",draw_sensor);

    document.getElementById("temp_min").addEventListener("change",function(ev) { ranges[0][0]=parseFloat(ev.srcElement.value); inner_draw_sensor(current_sensor);});
    document.getElementById("temp_max").addEventListener("change",function(ev) { ranges[0][1]=parseFloat(ev.srcElement.value); inner_draw_sensor(current_sensor); });
    document.getElementById("turbid_min").addEventListener("change",function(ev) { ranges[1][0]=parseFloat(ev.srcElement.value); console.log(current_sensor); inner_draw_sensor(current_sensor); });
    document.getElementById("turbid_max").addEventListener("change",function(ev) { ranges[1][1]=parseFloat(ev.srcElement.value); inner_draw_sensor(current_sensor); });
    document.getElementById("pm_min").addEventListener("change",function(ev) { ranges[2][0]=parseFloat(ev.srcElement.value); inner_draw_sensor(current_sensor); });
    document.getElementById("pm_max").addEventListener("change",function(ev) { ranges[2][1]=parseFloat(ev.srcElement.value); inner_draw_sensor(current_sensor); });

    document.getElementById("points").addEventListener("click",draw_viz);
    document.getElementById("heatline").addEventListener("click",draw_viz);
    
    document.getElementById("t1").addEventListener("click",draw_trip);
    document.getElementById("t2").addEventListener("click",draw_trip);
    document.getElementById("t3").addEventListener("click",draw_trip);
    document.getElementById("t4").addEventListener("click",draw_trip);
    document.getElementById("t5").addEventListener("click",draw_trip);
    document.getElementById("t6").addEventListener("click",draw_trip);

    document.getElementById("none").addEventListener("click",clear_hex);
    
    ["mean_temp_hex_falmouth",
     "mean_temp_hex_helford",
     "mean_turbidity_hex_falmouth",
     "mean_turbidity_hex_helford",
     "mean_pm1_std_hex_falmouth",
     "mean_pm1_std_hex_helford",
     "mean_pm25_std_hex_falmouth",
     "mean_pm25_std_hex_helford",
     "mean_pm10_std_hex_falmouth",
     "mean_pm10_std_hex_helford",
     "mean_p_rms_std_hex_helford",
     "mean_tol_cf_125hz_std_hex_helford",
     "mean_small_boats_hex_helford",
     "mean_big_boats_hex_helford",
     "mean_large_ships_hex_helford"].forEach(function(hexname) {
	 document.getElementById(hexname).addEventListener("click",draw_hex);
     });
    
    var legend = L.control({position: 'bottomleft'});
    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
	div.id="scale";
	_update_scale(div);
        return div;
    };

    legend.addTo(map);

    
    //add scale bar
    L.control.scale().addTo(map);





    

});
