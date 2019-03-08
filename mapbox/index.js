mapboxgl.accessToken = 'pk.eyJ1IjoieGllZ3Vkb25nNDU2IiwiYSI6ImNqczUyczJ1NzBiZDM0NG5peDV1MGc0OHgifQ.zqfiaGVaYRrjY--NLs9kxw';

var map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/mapbox/streets-v9',
    center: [237.66921043396, 47.604889909932865],
    zoom: 10
});


// Datasets
var sidewalks = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/' +
    'master/data_table/sidewalks.geojson'
var crossings = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/' +
    'master/data_table/crossings.geojson'
var hospitals = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/' +
    'master/data_table/Hospitals.geojson'
var dog_off_leash_areas = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/' +
    'master/data_table/Seattle%20Parks%20and%20Recreation%20GIS%20Map%20Layer' +
    '%20Shapefile%20-%20Dog%20Off%20Leash%20Areas.geojson'
var drinking_fountains = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/' +
    'master/data_table/Seattle%20Parks%20and%20Recreation%20GIS%20Map%20Layer%20' +
    'Shapefile%20-%20Drinking%20Fountain.geojson'
var public_restrooms = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/master/data_table/' +
    'Seattle%20Parks%20and%20Recreation%20GIS%20Map%20Layer%20Shapefile%20-%20' +
    'Public%20Restroom.geojson'
var view_points = 'https://raw.githubusercontent.com/robin-qu/City-scale-Analytics/master/data_table/' +
    'Seattle%20Parks%20and%20Recreation%20GIS%20Map%20Layer%20Shapefile%20-%20View%20Points.geojson'
var walkshed = 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/' +
    'shenghao/walkshed%20test/test_walkshed.geojson'

// Add datasets
map.on('load', function() {
    function addLine(file, id, color, line_width) {
        map.addLayer({
            id: id,
            type: 'line',
            source: {
                type: 'geojson',
                data: file
            },
            paint: {
                'line-color': color,
                'line-width': line_width
            }
        })
    }

    function addPoints(file, source, id, color) {
        map.addSource(source, {
            type: "geojson",
            data: file,
            cluster: true,
            clusterMaxZoom: 14,
            clusterRadius: 50
        });

        map.addLayer({
            id: id,
            type: "circle",
            source: source,
            filter: ["has", "point_count"],
            paint: {
                "circle-color": color,
                "circle-radius": [
                    "step",
                    ["get", "point_count"],
                    20,
                    50,
                    30,
                    200,
                    40
                ]
            }
        });

        map.addLayer({
            id: "unclustered " + id,
            type: "circle",
            source: source,
            filter: ["!", ["has", "point_count"]],
            paint: {
                "circle-color": color,
                "circle-radius": 5,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#000000"
            }
        });

        map.addLayer({
            id: id + "text",
            type: "symbol",
            source: source,
            filter: ["has", "point_count"],
            layout: {
                "text-field": "{point_count_abbreviated}",
                "text-font": ["DIN Offc Pro Medium", "Arial Unicode MS Bold"],
                "text-size": 12
            }
        });

        // inspect a cluster on click
        map.on('click', id, function (e) {
            var features = map.queryRenderedFeatures(e.point, { layers: [id] });
            var clusterId = features[0].properties.cluster_id;
            map.getSource(source).getClusterExpansionZoom(clusterId, function (err, zoom) {
                if (err)
                    return;

                map.easeTo({
                    center: features[0].geometry.coordinates,
                    zoom: zoom
                });
            });
        });

        map.on('mouseenter', id, function () {
            map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', id, function () {
            map.getCanvas().style.cursor = '';
        });
    }

    //visualize
    addLine(sidewalks, 'Sidewalks', '#000000', 1)
    addLine(crossings, 'Crossings', '#FF0000', 1)
    addLine(walkshed, 'Walkshed', '#0000FF', 6)
    addPoints(dog_off_leash_areas, 'dola', 'Dog Off Leash Areas', '#006400')
    addPoints(public_restrooms, 'pr', 'Public Restrooms', '#4B0082')
    addPoints(drinking_fountains, 'df', 'Drinking Fountains', '#6495ED')
    addPoints(view_points, 'vp', 'View Points', '#FFD700')
    addPoints(hospitals, 'hsp', 'Hospitals', '#FF1493')
});


// Filter features by toggling a list
var marker;
var toggleableLayerIds = ['Drinking Fountains',
                          'Dog Off Leash Areas',
                          'Hospitals',
                          'Public Restrooms',
                          'View Points'];

for (var i = 0; i < toggleableLayerIds.length; i++) {
	var id = toggleableLayerIds[i];

	var link = document.createElement('a');
	link.href = '#';
	link.className = 'active';
	link.textContent = id;
    link.uncluster = "unclustered " + id;
    link.numbertext = id + "text";

	link.onclick = function (e) {
		var clickedLayer = this.textContent;
        var clickedLayer2 = this.uncluster;
        var clickedLayer3 = this.numbertext;
		e.preventDefault();
		e.stopPropagation();

		var visibility = map.getLayoutProperty(clickedLayer, 'visibility');

		if (visibility === 'visible') {
			map.setLayoutProperty(clickedLayer, 'visibility', 'none');
            map.setLayoutProperty(clickedLayer2, 'visibility', 'none');
            map.setLayoutProperty(clickedLayer3, 'visibility', 'none');
			this.className = '';
		} else {
			this.className = 'active';
			map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
            map.setLayoutProperty(clickedLayer2, 'visibility', 'visible');
            map.setLayoutProperty(clickedLayer3, 'visibility', 'visible');
		}
	};

	var layers = document.getElementById('menu');
	layers.appendChild(link);
}


// Add Zoom-in, Zoom-out button
map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');


// access current location
map.addControl(new mapboxgl.GeolocateControl({
	positionOptions: {
		enableHighAccuracy: true
	},
	trackUserLocation: true
}), 'bottom-left');


//show lat and long in console
map.on('click', function(e) {
	var isClicked = false;

	const result = map.queryRenderedFeatures(e.point, {layers:['sidewalk']});
	if (!isClicked && result.length > 0) {
		marker = new mapboxgl.Marker(e).setLngLat(e.lngLat).addTo(map);
		isClicked = true;
	} else if (isClicked) {
		marker.remove();
		isClicked = false;
	}

	console.log(isClicked);
	console.log('click', e.lngLat);
})
