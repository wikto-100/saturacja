var saturationMarkers = {};
L.drawLocal = L.drawLocal || {};

L.drawLocal.draw = L.drawLocal.draw || {};
L.drawLocal.draw.toolbar = {
  actions: {
    title: 'Anuluj rysowanie',
    text: 'Anuluj'
  },
  finish: {
    title: 'Zakończ rysowanie',
    text: 'Zakończ'
  },
  undo: {
    title: 'Usuń ostatni punkt',
    text: 'Usuń'
  },
  buttons: {
    polygon: 'Narysuj wielokąt',
    polyline: 'Narysuj linię',
    rectangle: 'Narysuj prostokąt',
    circle: 'Narysuj okrąg',
    marker: 'Umieść marker'
  }
};

L.drawLocal.draw.handlers = L.drawLocal.draw.handlers || {};
L.drawLocal.draw.handlers.polygon = {
  tooltip: {
    start: 'Kliknij, aby rozpocząć rysowanie wielokąta.',
    cont: 'Kliknij, aby dodać kolejny punkt.',
    end: 'Kliknij pierwszy punkt, aby zakończyć rysowanie.'
  }
};

L.drawLocal.edit = L.drawLocal.edit || {};
L.drawLocal.edit.toolbar = {
  actions: {
    save: {
      title: 'Zapisz zmiany',
      text: 'Zapisz'
    },
    cancel: {
      title: 'Anuluj edycję, odrzuć zmiany',
      text: 'Anuluj'
    },
    clearAll: {
      title: 'Wyczyść wszystkie warstwy',
      text: 'Wyczyść'
    }
  },
  buttons: {
    edit: 'Edytuj warstwy',
    remove: 'Usuń warstwy'
  }
};

L.drawLocal.edit.handlers = L.drawLocal.edit.handlers || {};
L.drawLocal.edit.handlers.edit = {
  tooltip: {
    text: 'Przeciągnij punkt, aby edytować kształt.',
    subtext: 'Kliknij anuluj, aby odrzucić zmiany.'
  }
};
L.drawLocal.edit.handlers.remove = {
  tooltip: {
    text: 'Kliknij na element, aby go usunąć.'
  }
};

/******************************************************
 * 1. Marker: Popup & Edit Form Handling (Polish UI)  *
 ******************************************************/
function createEditFormHtml(properties) {
    return `
      <div class="edit-form">
        <label for="edit-status">Status:</label>
        <select id="edit-status">
          <option value="active" ${properties.status === 'active' ? 'selected' : ''}>Aktywny</option>
          <option value="inactive" ${properties.status === 'inactive' ? 'selected' : ''}>Nieaktywny</option>
        </select>
        <label for="edit-city">Miejscowość:</label>
        <input type="text" id="edit-city" value="${properties.city || ''}" />
        <label for="edit-street">Ulica:</label>
        <input type="text" id="edit-street" value="${properties.street_name || ''}" />
        <label for="edit-street_no">Nr domu:</label>
        <input type="text" id="edit-street_no" value="${properties.street_no || ''}" />
        <label for="edit-local">Mieszkanie:</label>
        <input type="text" id="edit-local" value="${properties.local || ''}" />
        <label for="edit-phone">Telefon:</label>
        <input type="text" id="edit-phone" value="${properties.phone || ''}" />
        <label for="edit-email">Email:</label>
        <input type="text" id="edit-email" value="${properties.email || ''}" />
        <label for="edit-note">Notatka:</label>
        <textarea id="edit-note">${properties.note || ''}</textarea>
        <div class="form-actions">
            <button class="btn btn-sm btn-primary save-edit">Zapisz</button>
        </div>
      </div>
    `;
}



function getMarkerPopupContent(properties) {
    var content = `<div class="popup-content">
      <div class="popup-row">
        <span class="label">Status:</span>
        <span class="value">${properties.status === 'active' ? "Aktywny" : "Nieaktywny"}</span>
      </div>
      <div class="popup-row">
        <span class="label">Adres:</span>
        <span class="value">${properties.street_name || ''} ${properties.street_no || ''}, ${properties.city || ''} ${properties.local ? "(" + properties.local + ")" : ""}</span>
      </div>`;
    if (properties.phone && properties.phone.trim() !== "") {
        content += `<div class="popup-row">
                      <span class="label">Telefon:</span>
                      <span class="value">${properties.phone}</span>
                    </div>`;
    }
    if (properties.email && properties.email.trim() !== "") {
        content += `<div class="popup-row">
                      <span class="label">Email:</span>
                      <span class="value">${properties.email}</span>
                    </div>`;
    }
    if (properties.note && properties.note.trim() !== "") {
        content += `<div class="popup-row">
                      <span class="label">Notatka:</span>
                      <span class="value">${properties.note}</span>
                    </div>`;
    }
    if (properties.created_at) {
        var date = new Date(properties.created_at);
        content += `<div class="popup-row">
                      <span class="label">Utworzono:</span>
                      <span class="value">${date.toLocaleString("pl-PL")}</span>
                    </div>`;
    }
    content += `<div class="popup-row">
                  <button class="btn btn-xs btn-primary edit-btn">Edytuj</button>
                </div>
              </div>`;
    return content;
}



function bindMarkerEditEvents(layer) {
    // Remove existing handlers to avoid double-binding
    layer.off('popupopen');
    layer.off('popupclose');

    layer.on('popupopen', function () {
        var popupEl = layer.getPopup().getElement();
        var editBtn = popupEl.querySelector('.edit-btn');
        if (!editBtn) return;

        editBtn.addEventListener('click', function () {
            var currentProps = layer.feature.properties;
            layer.setPopupContent(createEditFormHtml(currentProps));

            var saveBtn = layer.getPopup().getElement().querySelector('.save-edit');
            saveBtn.addEventListener('click', function () {
                var popupElement = layer.getPopup().getElement();
                var updatedData = {
                    id: layer.feature.id,  // assuming feature.id = Customer ID
                    status: popupElement.querySelector('#edit-status').value,
                    city: popupElement.querySelector('#edit-city').value,
                    street_name: popupElement.querySelector('#edit-street').value,
                    street_no: popupElement.querySelector('#edit-street_no').value,
                    local: popupElement.querySelector('#edit-local').value,
                    phone: popupElement.querySelector('#edit-phone').value,
                    email: popupElement.querySelector('#edit-email').value,
                    note: popupElement.querySelector('#edit-note').value,
                };

                fetch('/api/update_client', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updatedData)
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            layer.feature.properties = Object.assign(layer.feature.properties, data.client);
                            if (layer.feature.properties.status === "active") {
                                layer.setStyle({ color: 'green', fillColor: 'green' });
                            } else {
                                layer.setStyle({ color: 'red', fillColor: 'red' });
                            }
                            layer.setPopupContent(getMarkerPopupContent(layer.feature.properties));
                            bindMarkerEditEvents(layer);
                            layer.closePopup();
                        } else {
                            updateError("Błąd przy aktualizacji danych: " + (data.error || ""));
                            layer.setPopupContent("Błąd przy aktualizacji danych");
                            bindMarkerEditEvents(layer);
                        }
                    })
                    .catch(error => {
                        console.error("Błąd przy zapisie zmian:", error);
                        updateError("Błąd przy zapisie zmian: " + error);
                        layer.setPopupContent("Błąd przy zapisie zmian");
                        bindMarkerEditEvents(layer);
                    });
            }, { once: true });
        }, { once: true });
    });

    layer.on('popupclose', function () {
        layer.setPopupContent(getMarkerPopupContent(layer.feature.properties));
        bindMarkerEditEvents(layer);
    });
}

function onEachMarker(feature, layer) {
    layer.bindPopup(getMarkerPopupContent(feature.properties));
    bindMarkerEditEvents(layer);
}

/*********************************
 * 3. Polygon Popup Functionality *
 *********************************/
function getPolygonPopupHTML() {
    return `
      <button class="btn btn-sm btn-primary import-btn">Importuj adresy</button>
      <button class="btn btn-sm btn-danger delete-btn">Usuń adresy</button>
      <button class="btn btn-sm btn-warning measure-btn">Pomiar</button>
      `;
}
function pointInPolygon(point, polyPoints) {
    var x = point.lng, y = point.lat;
    var inside = false;
    for (var i = 0, j = polyPoints.length - 1; i < polyPoints.length; j = i++) {
        var xi = polyPoints[i].lng, yi = polyPoints[i].lat;
        var xj = polyPoints[j].lng, yj = polyPoints[j].lat;
        var intersect = ((yi > y) !== (yj > y)) &&
            (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function bindPolygonPopup(layer, polygonCoords) {
    layer.bindPopup(getPolygonPopupHTML());
    layer.off('popupopen');
    layer.on('popupopen', function () {
        var popupEl = layer.getPopup().getElement();
        var importBtn = popupEl.querySelector('.import-btn');
        var deleteBtn = popupEl.querySelector('.delete-btn');
        var measureBtn = popupEl.querySelector('.measure-btn');

        if (importBtn) {
            importBtn.addEventListener('click', function () {
                layer.closePopup();
                loadingOverlay.style.display = "flex";
                fetch('/api/inactive_addresses?polygon=' + encodeURIComponent(polygonCoords))
                    .then(response => response.json())
                    .then(data => {
                        loadingOverlay.style.display = "none";
                        if (data.error) {
                            updateError(data.error);
                            return;
                        } else {
                            updateError(""); // Clear previous error
                        }
                        if (layer.importedLayer) {
                            map.removeLayer(layer.importedLayer);
                        }
                        layer.importedLayer = L.geoJSON(data, {
                            pointToLayer: function (feature, latlng) {
                                return L.circleMarker(latlng, {
                                    radius: 5,
                                    color: 'red',
                                    weight: 1,
                                    fillColor: 'red',
                                    fillOpacity: 0.6
                                });
                            },
                            onEachFeature: function (feature, lyr) {
                                lyr.bindPopup(
                                    "Nieaktywny: " + feature.properties.street_name + " " +
                                    feature.properties.street_no + ", " + feature.properties.city
                                );
                            }
                        }).addTo(map);
                        bindPolygonPopup(layer, polygonCoords);
                    })
                    .catch(error => {
                        loadingOverlay.style.display = "none";
                        console.error("Błąd przy pobieraniu adresów:", error);
                        updateError("Błąd przy pobieraniu adresów: " + error);
                        layer.setPopupContent("Błąd przy pobieraniu adresów");
                        setTimeout(function () {
                            layer.setPopupContent(getPolygonPopupHTML());
                            bindPolygonPopup(layer, polygonCoords);
                        }, 2000);
                    });
            }, { once: true });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', function () {
                if (!confirm("Czy na pewno chcesz usunąć nieaktywne adresy w tym obszarze?")) return;
                layer.closePopup();
                loadingOverlay.style.display = "flex";
                fetch('/api/delete_inactive_addresses?polygon=' + encodeURIComponent(polygonCoords))
                    .then(response => response.json())
                    .then(data => {
                        loadingOverlay.style.display = "none";
                        if (data.error) {
                            updateError(data.error);
                            return;
                        } else {
                            updateError("");
                        }
                        if (layer.importedLayer) {
                            map.removeLayer(layer.importedLayer);
                            layer.importedLayer = null;
                        }

                        var polyPoints = polygonCoords.split(",").map(function (pair) {
                            var parts = pair.trim().split(" ");
                            return L.latLng(parseFloat(parts[0]), parseFloat(parts[1]));
                        });
                        // Remove red markers (inactive clients) from inactiveLayer that are inside the polygon.
                        inactiveLayer.eachLayer(function (marker) {
                            if (pointInPolygon(marker.getLatLng(), polyPoints)) {
                                inactiveLayer.removeLayer(marker);
                            }
                        });


                        layer.setPopupContent("Nieaktywne adresy usunięte.");
                        setTimeout(function () {
                            layer.setPopupContent(getPolygonPopupHTML());
                            bindPolygonPopup(layer, polygonCoords);
                        }, 2000);
                    })
                    .catch(error => {
                        loadingOverlay.style.display = "none";
                        console.error("Błąd przy usuwaniu adresów:", error);
                        updateError("Błąd przy usuwaniu adresów: " + error);
                        layer.setPopupContent("Błąd przy usuwaniu adresów");
                        setTimeout(function () {
                            layer.setPopupContent(getPolygonPopupHTML());
                            bindPolygonPopup(layer, polygonCoords);
                        }, 2000);
                    });
            }, { once: true });
        }

        if (measureBtn) {
            measureBtn.addEventListener('click', function () {
                layer.closePopup();
                loadingOverlay.style.display = "flex";
                fetch('/api/measure_saturation?polygon=' + encodeURIComponent(polygonCoords))
                    .then(response => response.json())
                    .then(data => {
                        loadingOverlay.style.display = "none";
                        if (data.error) {
                            updateError(data.error);
                            return;
                        } else {
                            updateError("");
                        }
                        var center = data.center; // {lon, lat}
                        var saturationMarker = L.circleMarker([center.lat, center.lon], {
                            radius: 8,
                            color: 'orange',
                            fillColor: 'orange',
                            fillOpacity: 0.8
                        }).addTo(map);

                        saturationMarkers[data.saturation_id] = saturationMarker;
                        var date = new Date();
                        var popupContent = "Pomiar saturacji<br/>" +
                            "Aktywni: " + data.active + "<br/>" +
                            "Nieaktywni: " + data.inactive + "<br/>" +
                            "Saturacja: " + data.ratio * 100 + "%" + "<br/>" +
                            "Utworzono: " + date.toLocaleString("pl-PL") + "<br/>" +
                            "<button class='btn btn-sm btn-danger delete-saturation-btn' data-id='" + data.saturation_id + "'>Usuń pomiar</button>";

                        saturationMarker.bindPopup(popupContent).openPopup();
                    })
                    .catch(error => {
                        loadingOverlay.style.display = "none";
                        console.error("Błąd przy pomiarze saturacji:", error);
                        updateError("Błąd przy pomiarze saturacji: " + error);
                    });
            }, { once: true });
        }
    });
}

// Helper function to update error messages on the page.
function updateError(msg) {
    if (errorDiv) {
        if (msg && msg.trim() !== "") {
            errorDiv.style.display = "block";
            errorDiv.innerText = msg;
            // Hide the error after 10 seconds
            setTimeout(function () {
                errorDiv.style.display = "none";
                errorDiv.innerText = "";
            }, 10000);
        } else {
            errorDiv.style.display = "none";
            errorDiv.innerText = "";
        }
    }
}

/*****************************************
 * 2. Map Setup and Main Initialization  *
 *****************************************/
var map = L.map('map').setView([52.2297, 21.0122], 6);

// Caching references for performance
var errorDiv = document.getElementById("error-message");
var loadingOverlay = document.getElementById("loadingOverlay");

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

L.Control.geocoder({
    defaultMarkGeocode: false
})
    .on('markgeocode', function (e) {
        var center = e.geocode.center;
        map.setView(center, 18);
        L.popup()
            .setLatLng(center)
            .setContent(e.geocode.name)
            .openOn(map);
    })
    .addTo(map);

var activeLayer = L.geoJSON(activeData, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            radius: 5,
            color: 'green',
            weight: 1,
            fillColor: 'green',
            fillOpacity: 0.6
        });
    },
    onEachFeature: onEachMarker
}).addTo(map);

var inactiveLayer = L.geoJSON(inactiveData, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
            radius: 5,
            color: 'red',
            weight: 1,
            fillColor: 'red',
            fillOpacity: 0.6
        });
    },
    onEachFeature: onEachMarker
}).addTo(map);

// Setup a dedicated pane for polygons
var polygonPane = map.createPane('polygonPane');
polygonPane.style.zIndex = 350;

var drawnItems = new L.FeatureGroup([], { pane: 'polygonPane' });
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    draw: {
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
        polygon: {
            allowIntersection: false,
            showArea: true,
            drawError: {
                color: '#e1e100',
                message: '<strong>Error:</strong> cannot draw that shape!'
            },
            shapeOptions: { color: 'red' }
        }
    },
    edit: { featureGroup: drawnItems }
});
map.addControl(drawControl);

// Helper to get polygon coordinates from layer
function getPolygonCoords(layer) {
    var latlngs = layer.getLatLngs()[0];
    return latlngs.map(function (latlng) {
        return latlng.lat + " " + latlng.lng;
    }).join(",");
}

// Draw event
map.on('draw:created', function (e) {
    var layer = e.layer;
    drawnItems.addLayer(layer);
    var polygonCoords = getPolygonCoords(layer);
    bindPolygonPopup(layer, polygonCoords);
});

// Edit event
map.on('draw:edited', function (e) {
    e.layers.eachLayer(function (layer) {
        var polygonCoords = getPolygonCoords(layer);
        bindPolygonPopup(layer, polygonCoords);
    });
});


// Combine everything else into one DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
    // 1. Fetch & display saturation markers from server on load.
    fetch('/api/saturation_markers')
        .then(response => response.json())
        .then(data => {
            L.geoJSON(data, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, {
                        radius: 8,
                        color: 'orange',
                        fillColor: 'orange',
                        fillOpacity: 0.8
                    });
                },
                onEachFeature: function (feature, layer) {
                    var date = new Date(feature.properties.computed_at);
                    layer.bindPopup(
                        "Pomiar saturacji<br/>" +
                        "Aktywni: " + feature.properties.active + "<br/>" +
                        "Nieaktywni: " + feature.properties.inactive + "<br/>" +
                        "Saturacja: " + feature.properties.ratio * 100 + "%" + "<br/>" +
                        "Utworzono: " + date.toLocaleString("pl-PL") + "<br/>" +
                        "<button class='btn btn-sm btn-danger delete-saturation-btn' data-id='" + feature.properties.id + "'>Usuń pomiar</button>"
                    );
                    if (feature.properties && feature.properties.id) {
                        saturationMarkers[feature.properties.id] = layer;
                    }
                }
            }).addTo(map);
        })
        .catch(error => {
            console.error("Błąd przy pobieraniu markerów saturacji:", error);
        });

    // 2. Handle click on “Usuń pomiar” for saturation markers
    document.addEventListener("click", function (e) {
        if (e.target && e.target.classList.contains("delete-saturation-btn")) {
            var saturationId = e.target.getAttribute("data-id");
            if (!saturationId || saturationId === "undefined") {
                updateError("Nieprawidłowy identyfikator pomiaru.");
                return;
            }
            fetch("/api/delete_saturation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: parseInt(saturationId) })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (saturationMarkers[saturationId]) {
                            map.removeLayer(saturationMarkers[saturationId]);
                            delete saturationMarkers[saturationId];
                        }
                    } else {
                        alert("Błąd przy usuwaniu pomiaru: " + (data.error || "Nieznany błąd."));
                    }
                })
                .catch(error => {
                    console.error("Błąd przy usuwaniu pomiaru:", error);
                    alert("Błąd przy usuwaniu pomiaru: " + error);
                });
        }
    });

    // 3. CSV Import functionality
    var importBtn = document.getElementById("import-btn");
    var csvInput = document.getElementById("csv-file-input");

    // Get csrf token helper
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie("csrftoken");

    if (importBtn && csvInput) {
        importBtn.addEventListener("click", function () {
            csvInput.click();
        });

        csvInput.addEventListener("change", function () {
            if (csvInput.files.length > 0) {
                var file = csvInput.files[0];
                var formData = new FormData();
                formData.append("file", file);

                loadingOverlay.style.display = "flex";
                fetch("/api/import_clients", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": csrftoken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        loadingOverlay.style.display = "none";
                        if (data.error) {
                            updateError(data.error);
                        } else if (data.success) {
                            updateError(""); // clear error
                            alert("Klienci zaktualizowani pomyślnie.");
                            location.reload();
                        } else {
                            updateError("Nieznany błąd podczas importu.");
                        }
                    })
                    .catch(error => {
                        loadingOverlay.style.display = "none";
                        console.error("Błąd importowania:", error);
                        updateError("Podczas importowania wystąpił błąd: " + error);
                    });
            }
        });
    }

    // 4. CSV Export functionality
    var exportBtn = document.getElementById("export-btn");
    var exportForm = document.getElementById("export-form");

    if (exportBtn) {
        exportBtn.addEventListener("click", function () {
            var exportModalEl = document.getElementById("exportModal");
            var exportModal = new bootstrap.Modal(exportModalEl);
            exportModal.show();
        });
    }

    if (exportForm) {
        exportForm.addEventListener("submit", function (e) {
            e.preventDefault();
            var city = document.getElementById("export-city").value;
            var street = document.getElementById("export-street").value;
            var status = document.getElementById("export-status").value;
            var exportUrl = "/api/export_clients?city=" + encodeURIComponent(city) +
                "&street=" + encodeURIComponent(street) +
                "&status=" + encodeURIComponent(status);

            var exportModalEl = document.getElementById("exportModal");
            var exportModal = bootstrap.Modal.getInstance(exportModalEl);
            if (exportModal) {
                exportModal.hide();
            }
            window.location.href = exportUrl;
        });
    }

    var deptSwitch = document.getElementById("department-switch");
    if (deptSwitch) {
        deptSwitch.addEventListener("change", function() {
            var deptId = this.value;
            // Reload the page with the selected department id as a GET parameter.
            window.location.href = "?dept_id=" + deptId;
        });
    }


});
