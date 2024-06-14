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

// upload scenario as file type=standard
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

CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
});

// This will be triggered after challenge creation
$('#challenge-create-options #challenge_id').on('DOMSubtreeModified', function(){
  var params = {}
  // Step 0: retrieve challengeId provided by CTFd
  params['challengeId'] = $(this).val();

  // Step 1: Send the scenario file to CTFd
  const input = document.getElementById('scenario');
  const file = input.files[0]; // Get the first file selected 

  // define progress bar
  var pg = CTFd.ui.ezq.ezProgressBar({
    width: 0,
    title: "Sending scenario to chall-manager",
  });

  if (file) {
    sendFile(file).then(function(response) {
    console.log(response)
    params['scenarioId'] = response.data[0].id 

    pg = CTFd.ui.ezq.ezProgressBar({
      target: pg,
      width: 30,
    });
    
    // Step 2: Send the scenario file location to plugin that will create it on Chall-manager API
    console.log(params)

    CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/scenario", {
      method: 'POST',
      credentials: "same-origin",
      headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    }).then(function (a) {      
        return a.json();   
    }).then(function (json) {
      pg = CTFd.ui.ezq.ezProgressBar({
        target: pg,
        width: 100,
      });
      console.log(json)
      if (json.success){
        console.log(json.success)
        console.log(json.data.message.toString())
        setTimeout(function () {
          pg.modal("hide");
        }, 500);
        CTFd.ui.ezq.ezToast({
          title: "Success",
          body: "Scenario is upload on Chall-manager, hash : " + json.data.message.hash
      });
      }
    })});
  }

  
});