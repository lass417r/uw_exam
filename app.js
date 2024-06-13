let allCrimes = [];
let map;
let crimeMarkers = [];

/* ###################################################### */
/* Initialization of the Map and Fetching Initial Data */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize Mapbox map
  mapboxgl.accessToken = "pk.eyJ1IjoibGFzczc1MTkiLCJhIjoiY2xtJpMDIxZzNrbHdvbzA2ampicCJ9.2rXTAy83tB2ksh-bqr6STA";
  map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/outdoors-v12",
    center: [12.577013479674585, 55.65219273755571],
    zoom: 11.25,
    pitch: 35,
  });

  // Initialize the app by fetching initial crime data
  init();

  // Set up event listeners for UI interactions
  document.getElementById("refreshButton").addEventListener("click", function () {
    refreshDropdowns();
  });
  document.getElementById("crimeFilter").addEventListener("change", updateFilterButtonUrl);
  document.getElementById("severityFilter").addEventListener("change", updateFilterButtonUrl);
  document.getElementById("filterButton").addEventListener("click", updateFilters);
});

/* Function to Initialize the App and Fetch Initial Crime Data */
function init() {
  fetch("/api/crimes")
    .then((response) => response.json())
    .then((data) => {
      allCrimes = data;
      updateCrimeMarkers(allCrimes); // Initially display all markers
    })
    .catch((error) => console.error("Error loading initial crime data:", error));
}

/* ###################################################### */
/* Functions Related to Filtering and Updating Crime Markers */

/* Function to Update Filters and Refresh Crime Markers Based on Filters */
function updateFilters() {
  const typeFilter = document.querySelector("#crimeFilter").value;
  const severityFilter = document.querySelector("#severityFilter").value;

  const filteredCrimes = allCrimes.filter((crime) => {
    return (
      (typeFilter === "all" || crime.crime.crime_type === typeFilter) && (severityFilter === "all" || crime.crime.crime_severity === severityFilter)
    );
  });

  updateCrimeMarkers(filteredCrimes);
}

/* Function to Update Crime Markers on the Map */
function updateCrimeMarkers(crimes) {
  clearMarkers();

  crimes.forEach((crime) => {
    const crimeLngLat = [crime.crime.longitude, crime.crime.latitude];
    const marker = new mapboxgl.Marker().setLngLat(crimeLngLat).addTo(map);

    const crimeId = crime.crime._key;
    marker._element.innerHTML = `<button class="btn_crime" mix-get="/crimes/${crimeId}" onclick="mixhtml(); return false"><div style="pointer-events:none">${marker._element.innerHTML}</div></button>`;

    crimeMarkers.push(marker);
  });
}

/* Function to Clear Existing Crime Markers from the Map */
function clearMarkers() {
  crimeMarkers.forEach((marker) => marker.remove());
  crimeMarkers = [];
}

/* ###################################################### */
/* Functions Related to UI Interaction */

/* Function to Refresh Dropdowns and Reset Filters */
function refreshDropdowns() {
  document.getElementById("crimeFilter").selectedIndex = 0;
  document.getElementById("severityFilter").selectedIndex = 0;
  updateFilters();
}

/* Function to Update Filter Button URL Based on Selected Filters */
function updateFilterButtonUrl() {
  const crimeType = document.getElementById("crimeFilter").value;
  const crimeSeverity = document.getElementById("severityFilter").value;
  const url = `/filtered-crimes?type=${crimeType}&severity=${crimeSeverity}`;

  const filterButton = document.getElementById("filterButton");
  filterButton.setAttribute("mix-get", url);
}

/* Function to Toggle Content Visibility */
function toggleContent(id, buttonId) {
  var contentElement = document.getElementById(id);
  var buttonElement = document.getElementById(buttonId);

  if (contentElement.classList.contains("hidden")) {
    contentElement.classList.remove("hidden");
    buttonElement.querySelector(".arrow").classList.add("arrow-up");
    buttonElement.querySelector(".arrow").classList.remove("arrow-down");
  } else {
    contentElement.classList.add("hidden");
    buttonElement.querySelector(".arrow").classList.add("arrow-down");
    buttonElement.querySelector(".arrow").classList.remove("arrow-up");
  }
}
