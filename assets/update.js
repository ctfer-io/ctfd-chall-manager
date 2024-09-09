
// selector for update-strategy
function displayUpdateStrategy() {
  document.getElementById('update-strategy-div').style.display = 'block'; 
}


// auto send the scenario and display the update-strategy-div
document.getElementById('scenario').addEventListener('change', function(event) {
  if (event.target.files.length > 0) {
      // send file and get filesId
      if (document.getElementById('scenario_id').value) {
        // delete previous file upload
        deleteFile(document.getElementById('scenario_id').value)
      }

      displayUpdateStrategy()

      sendFile(event.target.files[0]).then(function(response) {
        document.getElementById('scenario_id').value = response.data[0].id ;
      });

  }
});


// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  console.log("pouet")
  var datetimeLocal = document.getElementById("until-input-local").value;  
  if (datetimeLocal != "") {
    var datetimeUTC =(new Date(datetimeLocal)).toISOString();
    document.getElementById("until-input-utc").value = datetimeUTC;
  } else {
    document.getElementById("until-input-utc").value = ""
  }
});

// display current scenario file
function displayCurrentScenario() {
    scenario_id_div = document.getElementById('current-scenario-id')
    CTFd.fetch("/api/v1/files/" + scenario_id_div.innerText, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: "same-origin",
      }).then(function (a) {
        return a.json();
      })
      .then(function (json) {
          console.log(json.data.location)
          scenario_location = json.data.location
          scenario_file_div = document.getElementById('scenario_file')
          scenario_name = scenario_location.split('/')[1]
          scenario_file_div.innerHTML = '<a href="/files/' + scenario_location + '">' + scenario_name + '</a>'
      })
};

function sendFile(file){
  return new Promise(function(resolve, reject) {
    var formData = new FormData();
    formData.append('file', file);
    formData.append('nonce', CTFd.config.csrfNonce);
    formData.append('type', 'standard') // explicit configuration

    $.ajax({
      url: '/api/v1/files',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      credentials: 'same-origin', // Include credentials
      success: function(response){
        resolve(response); // Résoudre la promesse avec la réponse de la requête AJAX
      },
      error: function(xhr, status, error){
        reject(error); // Rejeter la promesse avec l'erreur de la requête AJAX
      }
    });
  });
}

function displayCurrentUntil() {
  var datetimeUTC = document.getElementById("until-input-utc").value; 
  if (datetimeUTC) {
    var datetimeLocal = new Date(datetimeUTC);

    // Format the local date to match 'datetime-local' input format
    var formattedLocalDate = datetimeLocal.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:mm

    // Set the formatted local date to the datetime-local input
    document.getElementById("until-input-local").value = formattedLocalDate;
  }
}

displayCurrentUntil()
displayCurrentScenario()

