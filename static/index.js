mapboxgl.accessToken = 'pk.eyJ1IjoieGllZ3Vkb25nNDU2IiwiYSI6ImNqczUyczJ1NzBiZDM0NG5peDV1MGc0OHgifQ.zqfiaGVaYRrjY--NLs9kxw';

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v9',
    center: [237.66921043396, 47.604889909932865],
    zoom: 10
});

// start point
var geocodes;

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
map.on('load', function () {
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

        // Create a popup
        var popup = new mapboxgl.Popup({
            closeButton: false,
            closeOnClick: false
        });

        map.on('mouseenter', 'unclustered ' + id, function (e) {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';

            var coordinates = e.features[0].geometry.coordinates.slice();
            if (id === "Hospitals") {
                var description = "Hospital: NAME: " + e.features[0].properties.FACILITY +
                    "; ADDRESS: " + e.features[0].properties.ADDRESS +
                    "; CITY: " + e.features[0].properties.CITY;
            } else if (id === "Public Restrooms") {
                var description = "Public Restroom: NAME: " + e.features[0].properties.alt_name +
                    "; PARK: " + e.features[0].properties.park +
                    "; DESCRIPTION: " + e.features[0].properties.descriptio;
            } else if (id === "Dog Off Leash Areas") {
                var description = "Dog Off Leash Area: NAME: " + e.features[0].properties.name;
            } else if (id === "Drinking Fountains") {
                var description = "Drinking Fountain: LOCATION: (" + e.features[0].geometry.coordinates + ")";
            } else {
                var description = "View Point: NAME: " + e.features[0].properties.name +
                    "; ADDRESS: " + e.features[0].properties.address;
            }

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup.setLngLat(coordinates)
                .setHTML(description)
                .addTo(map);
        });

        map.on('mouseleave', 'unclustered ' + id, function () {
            map.getCanvas().style.cursor = '';
            popup.remove();
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
            var features = map.queryRenderedFeatures(e.point, {layers: [id]});
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
    // addLine(walkshed, 'Walkshed', '#0000FF', 6)
    addPoints(dog_off_leash_areas, 'dola', 'Dog Off Leash Areas', '#008000')
    addPoints(public_restrooms, 'pr', 'Public Restrooms', '#8A2BE2')
    addPoints(drinking_fountains, 'df', 'Drinking Fountains', '#6495ED')
    addPoints(view_points, 'vp', 'View Points', '#FFD700')
    addPoints(hospitals, 'hsp', 'FF1493', '#FF1493')

    //////////////////////////////////////////////////////
    /////////       The Get Walkshed button      /////////
    //////////////////////////////////////////////////////
    document.getElementById("search").onclick = getFeature;

    function getFeature() {
        var feature = $("#featuresinput").text();
        var time = document.getElementById("timeinput").value;
        $.ajaxSetup({
            contentType: "application/json; charset=utf-8"
        });
        var request = {
            "start_lat": geocodes[0].center[1],
            "start_lon": geocodes[0].center[0],
            "max_time": time,
            "feature": feature,
        };
        // ajax the JSON to the server
        $.post("receiver", JSON.stringify(request), function (data) {
            console.log("request: " + request);
            console.log("Data: " + data);
            var mapLayer = map.getLayer('walkshed');
            if(typeof mapLayer !== 'undefined') {
              // Remove map layer & source.
              map.removeLayer('walkshed').removeSource('walkshed');
            }
            var walkshed = JSON.parse(data);
            addLine(walkshed, 'walkshed', '#6600cc', 6);

            document.getElementById('zoomto').addEventListener('click', function() {
                var lat = geocodes[0].center[1];
                var lon = geocodes[0].center[0];
                map.fitBounds([[
                    lon - 0.01,
                    lat - 0.01
                ], [
                    lon + 0.01,
                    lat + 0.01
                ]]);
            });

            // stop link reloading the page
            event.preventDefault();
        });
        // stop link reloading the page
        event.preventDefault();
    }

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
var nav = new mapboxgl.NavigationControl({position: 'bottom-right'});
map.addControl(nav);
nav._container.parentNode.className = "mapboxgl-ctrl-nav";

// access current location

var currentLocation = new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    },
    trackUserLocation: true
});

map.addControl(currentLocation);
currentLocation._container.parentNode.className = "mapboxgl-ctrl-currLocation";


//show lat and long in console
map.on('click', function (e) {
    const result = map.queryRenderedFeatures(e.point, {layers: ['Sidewalks']});
    if (result.length > 0) {
        if (typeof circleMarker !== "undefined") {
            circleMarker.remove();
        }
        //add marker
        console.log(typeof e.lngLat);
        circleMarker = new mapboxgl.Marker({color: "red"}).setLngLat(e.lngLat).addTo(map);
        geocodes = [];
        geocodes.push(coordinateFeature(e));
        console.log(geocodes);
        return geocodes;
        // console.log('click', e.lngLat);
    }


    function coordinateFeature(e) {
        return {
            center: [e.lngLat["lng"], e.lngLat["lat"]],
            geometry: {
                type: "Point",
                coordinates: [e.lngLat["lng"], e.lngLat["lat"]]
            },
            place_name: 'Lat: ' + e.lngLat["lat"] + ', Lng: ' + e.lngLat["lng"], // eslint-disable-line camelcase
            place_type: ['coordinate'], // eslint-disable-line camelcase
            properties: {},
            type: 'Feature'
        };
    }
});

var legend = document.getElementById('places-legend');


var legend = document.getElementById('places-legend');


