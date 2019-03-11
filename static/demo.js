mapboxgl.accessToken = 'pk.eyJ1IjoieGllZ3Vkb25nNDU2IiwiYSI6ImNqczUyczJ1NzBiZDM0NG5peDV1MGc0OHgifQ.zqfiaGVaYRrjY--NLs9kxw';
var map = mapboxgl.map('map', 'mapbox.streets').setView([38.91338, -77.03236], 16);

streetsBasemap = mapboxgl.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY2NhbnRleSIsImEiOiJjaWVsdDNubmEwMGU3czNtNDRyNjRpdTVqIn0.yFaW4Ty6VE3GHkrDvdbW6g', {
    maxZoom: 18,
    minZoom: 6,
    zIndex: 1,
    id: 'mapbox.streets'
}).addTo(map);

map.on('click', addMarker);

function addMarker(e){
  if (typeof circleMarker !== "undefined" ){
    map.removeLayer(circleMarker);
  }
  //add marker
  circleMarker = new  mapboxgl.circle(e.latlng, 200, {
                color: 'red',
                fillColor: '#f03',
                fillOpacity: 0.5
            }).addTo(map);
}
