// selector
document.getElementById('select-option').addEventListener('change', function() {
  var selectedOption = this.value;
  if (selectedOption === 'until') {
    document.getElementById('cm-mode-until').style.display = 'block';
    document.getElementById('cm-mode-timeout').style.display = 'none';
    document.getElementById('timeout-input').disabled = true;
    document.getElementById('until-input-local').disabled = false;
    document.getElementById('until-input-local').required = true;
    document.getElementById('timeout-input').value = ''; // Reset timeout input
  } else if (selectedOption === 'timeout') {
    document.getElementById('cm-mode-until').style.display = 'none';
    document.getElementById('cm-mode-timeout').style.display = 'block';
    document.getElementById('until-input-local').disabled = true;
    document.getElementById('timeout-input').disabled = false;
    document.getElementById('timeout-input').required = true;
    document.getElementById('until-input-local').value = ''; // Reset until input
  }
});

// convert Local into UTC
document.getElementById('until-input-local').addEventListener('change', function() {
  var datetimeLocal = document.getElementById("until-input-local").value;  
  var datetimeUTC =(new Date(datetimeLocal)).toISOString();
  document.getElementById("until-input-utc").value = datetimeUTC;
});

// display current scenario file
function displayScenario() {
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
function patchScenario() {
  const input = document.getElementById('scenario');
  const file = input.files[0]; // Get the first file selected

  var scenarioId = "";
  var params = {};

  if (file) {
    // Step 1: Send file
    sendFile(file).then(function(response) {
      scenarioId = response.data[0].id;

      // Step 2: Send the scenarioId to plugin that will update it on Chall-manager API
      if (scenarioId != "") {
        params = {
          "scenarioId": scenarioId
        };
      }

      console.log(params);
      CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/scenario?challengeId=" + CHALLENGE_ID, {
        method: 'PATCH',
        credentials: "same-origin",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      });
    });
  } else {
    // If no file is provided, call CTFd.fetch immediately
    console.log(params);
    CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/scenario?challengeId=" + CHALLENGE_ID, {
      method: 'PATCH',
      credentials: "same-origin",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    });
  }
}

// Detect if UPDATE button is trigger
function handleElementCreation(mutationsList, observer) {
  mutationsList.forEach(mutation => {
    mutation.addedNodes.forEach(node => {
      if (node.parentNode && node.parentNode.id === 'ezq--notifications-toast-container') {
        // Vérifier si un enfant de ezq--notifications-toast-container est créé
        console.log('Un enfant de ezq--notifications-toast-container a été créé !');
        // Appelez ici la fonction que vous souhaitez exécuter lorsque l'enfant est créé
        patchScenario();
      }
    });
  });
}


const parentElement = document.body;
const observerOptions = {
  childList: true, // Check childs (notification)
  subtree: true    // Check childs s(notification)
};

// Monitoring 
const observer = new MutationObserver(handleElementCreation);
observer.observe(parentElement, observerOptions);

displayScenario()


