mapboxgl.accessToken = 'pk.eyJ1IjoieGllZ3Vkb25nNDU2IiwiYSI6ImNqczUyczJ1NzBiZDM0NG5peDV1MGc0OHgifQ.zqfiaGVaYRrjY--NLs9kxw';

var bounds = [
	[-122.5063, 47.4849], // Southwest coordinates
	[-122.0877, 47.7425]  // Northeast coordinates
];

var map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/mapbox/streets-v9',
	center: [-122.3323077, 47.610582],
	zoom: 11,
	maxBounds: bounds
});


map.on('load', () => {
	// add hospitals
	map.addSource('hos', {
		type: 'geojson',
		data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/external_data/Hospitals.geojson',

	});

	map.addLayer({
		id: 'Hospitals',
		source: 'hos',
		type: 'circle',
		'layout': {
			'visibility': 'visible'
		},
		paint: {
			'circle-radius': 5,
			'circle-color': 'black'
		}
	});

	//add drinking_fountain
	map.addSource('df', {
		type: 'geojson',
		data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/external_data/Drinking%20Fountain.geojson'
	});

	map.addLayer({
		id: 'Drinking Fountains',
		source: 'df',
		type: 'circle',
		'layout': {
			'visibility': 'visible'
		},
		paint: {
			'circle-radius': 5,
			'circle-color': '#f08'
		}
	});

	//public restroom
	map.addSource('pr', {
		type: 'geojson',
		data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/external_data/Public%20Restroom.geojson'

	});

	map.addLayer({
		id: 'Public Restrooms',
		source: 'pr',
		type: 'circle',
		'layout': {
			'visibility': 'visible'
		},
		paint: {
			'circle-radius': 5,
			'circle-color': 'green'
		}
	});

	// dog off leash
	map.addSource('dol', {
		type: 'geojson',
		data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/external_data/Dog%20Off%20Leash%20Areas.geojson'

	});

	map.addLayer({
		id: 'Dog Off Leash Areas',
		source: 'dol',
		type: 'circle',
		'layout': {
			'visibility': 'visible'
		},
		paint: {
			'circle-radius': 5,
			'circle-color': '#F08080'
		}
	});

	// map.addSource('sp', {
	// 	type: 'geojson',
	// 	data: ''
	// });
	//
	// map.addLayer({
	// 	id: 'Start Point',
	// 	source: 'sp',
	// 	type: 'circle',
	//
	// });

	//public art
	// map.addSource('art', {
	// 	type: 'geojson',
	// 	data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/external_data/public_arts.geojson'
	//
	// });
	//
	// map.addLayer({
	// 	id: 'Public Arts',
	// 	source: 'art',
	// 	type: 'circle',
	// 	paint: {
	// 		'circle-radius': 5,
	// 		'circle-color': '#1313D1'
	// 	}
	// });

	//walkshed
	map.addLayer({
		id: 'walkshed',
		type: 'line',
		source: {
			type: 'geojson',
			data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/walkshed%20test/test_walkshed.geojson'
		},
		paint: {
			"line-color": "#000000",
			"line-width": 4
		}
	});

	// sidewalk
	map.addLayer({
		id: 'sidewalk',
		type: 'line',
		source: {
			type: 'geojson',
			data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/18%20AU/data_table/sidewalks.geojson'
		},
		paint: {
			"line-color": "#005EFF",
			"line-width": 1
		}
	});

	// crossing
	map.addLayer({
		id: 'crossing',
		type: 'line',
		source: {
			type: 'geojson',
			data: 'https://raw.githubusercontent.com/miss-grass/City-scale-Analytics/shenghao/18%20AU/data_table/crossings.geojson'
		},
		paint: {
			"line-color": "#FF00FF",
			"line-width": 1
		}
	});

});

var toggleableLayerIds = ['Drinking Fountains', 'Dog Off Leash Areas', 'Hospitals', 'Public Restrooms'];

for (var i = 0; i < toggleableLayerIds.length; i++) {
	var id = toggleableLayerIds[i];

	var link = document.createElement('a');
	link.href = '#';
	link.className = 'active';
	link.textContent = id;

	link.onclick = function (e) {
		var clickedLayer = this.textContent;
		e.preventDefault();
		e.stopPropagation();

		var visibility = map.getLayoutProperty(clickedLayer, 'visibility');

		if (visibility === 'visible') {
			map.setLayoutProperty(clickedLayer, 'visibility', 'none');
			this.className = '';
		} else {
			this.className = 'active';
			map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
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
	const result = map.queryRenderedFeatures(e.point, {layers:['sidewalk']});
	if (result.length > 0) {
		if (typeof circleMarker !== "undefined" ){
	    	circleMarker.remove();
	  	}
	  //add marker
	  	circleMarker = new mapboxgl.Marker({color:"red"}).setLngLat(e.lngLat).addTo(map);
		console.log('click', e.lngLat);
	}
});
