// getting activity data from python script app.py
fetch('/api/all_activities')
  .then(response => response.json())
  .then(data => map(data))
  .catch(error => {
    console.error('Error fetching data:', error);
  });

// initializing populating map by leaflet
function map(data){
    var map = L.map('map').setView([51.044922, -114.073746], 10);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    for(var x = 0; x < data.length; x++){
      var coordinates = L.Polyline.fromEncoded(data[x].map.summary_polyline).getLatLngs()
      var line_color
      var name = data[x].name
      var type = data[x].type
      var dist = data[x].distance / 1000
      var speed = data[x].average_speed * 3.6
      var elevation = data[x].total_elevation_gain

      if(type == 'Ride'){
        line_color = 'green'
      } else if(type == 'Run') {
        line_color = 'red'
      } else if(type == 'AlpineSki'){
        line_color = 'blue'
      } else if(type == 'NordicSki') {
        line_color = '#77C3EC'
      } else if(type == 'Hike') {
        line_color = 'brown'
      } else {
        line_color = 'black'
      }
     
      var activity = L.polyline(
        coordinates,
        {
          color: line_color,
          weight: 3,
          opacity: 1,
          lineJoin: 'round'
        }
      ).addTo(map)

      activity.bindPopup(name + "<br>" + type + "<br>" + (Math.round(dist * 100)/100) + " km <br>" + (Math.round(speed * 100)/100) + " km/h <br>"
        + elevation + " m");

    }
}

// accordian JS
var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    this.classList.toggle("active");

    /* Toggle between hiding and showing the active panel */
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}


