
CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
});

// This will be triggered after challenge creation
$('#challenge-create-options #challenge_id').on('DOMSubtreeModified', function(){
  // Step 0: retrieve challengeId provided by CTFd
  var challengeId = $(this).val();

  const CTFd = window.CTFd;

  // Step 1: Send the scenario file to CTFd
  const input = document.getElementById('scenario');
  const file = input.files[0]; // Get the first file selected

  if (file){
    var formData = new FormData();
    formData.append('file', file);
    formData.append("nonce", CTFd.config.csrfNonce);

    $.ajax({
      url: '/api/v1/files',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      credentials: 'same-origin', // Include credentials
      success: function(response){

        // Step 2: Send the scenario file location to plugin that will create it on Chall-manager API
          var scenario_location = response.data[0].location          
          var params = {
            "challengeId": challengeId,
            "scenario_location": scenario_location
          };

          return CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/admin/scenario", {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
          });
      },
      error: function(xhr, status, error){
          console.error('Error occurred while uploading file:', error);
      }
  });

  } 

  
});