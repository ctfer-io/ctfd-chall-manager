CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function () {
}

CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function () {
    loadInfo();
}

if (window.$ === undefined) window.$ = CTFd.lib.$;

function formatCountDown(countdown) {

    // Convert
    var seconds = Math.floor((countdown / 1000) % 60);
    var minutes = Math.floor((countdown / (1000 * 60)) % 60);
    var hours = Math.floor((countdown / (1000 * 60 * 60)) % 24);    
    var days = Math.floor((countdown / (1000 * 60 * 60 * 24 )) % 365);  

    // Build str
    var formattedCountdown = "" 
    
    if (days > 0) {
      formattedCountdown = formattedCountdown + days.toString() + "d " 
    }
    if (hours > 0 ){
      formattedCountdown = formattedCountdown + hours.toString().padStart(2, '0') + ":"
    }
    if (minutes > 0){
      formattedCountdown = formattedCountdown + minutes.toString().padStart(2, '0') + ":"
    }
    
    formattedCountdown = formattedCountdown + seconds.toString().padStart(2, '0');        

    return formattedCountdown;
}

function loadInfo() {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-chall-manager/instance?challengeId=" + challenge_id;


    CTFd.fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    }).then(function (response) {
        
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (window.t !== undefined) {
            clearInterval(window.t);
            window.t = undefined;
        }
        if (response.success) response = response.data;
        else CTFd._functions.events.eventAlert({
            title: "Fail",
            html: response.data.message,
        });
        $('#cm-panel-loading').hide();
        $('#cm-panel-until').hide(); 
       
        if (response.since && response.until) { // if instance has an until
           
            // check instance is not expired
            var now = new Date();
            var until = new Date(response.until)
            console.log(until)
            var count_down = until - now
            if (count_down > 0) {   // if the instance is not expired         
                
                $('#whale-panel-stopped').hide();
                $('#whale-panel-started').show();
                $('#whale-challenge-lan-domain').html(response.connectionInfo);                
                $('#whale-challenge-count-down').text(formatCountDown(count_down)); 
                $('#cm-panel-until').show();
                
                

                window.t = setInterval(() => {
                    count_down = until - new Date();
                    if (count_down <= 0) {
                        loadInfo();
                    }
                    $('#whale-challenge-count-down').text(formatCountDown(count_down));
                }, 1000);
            } else {
                $('#whale-panel-started').hide(); // hide the panel instance is up       
                $('#whale-panel-stopped').show(); // show the panel instance is down     
                $('#whale-challenge-lan-domain').html(''); 
            }
                    
        } else if (response.since) {    // if instance has no until
            $('#whale-panel-stopped').hide();
            $('#whale-panel-started').show();
            $('#whale-challenge-lan-domain').html(response.connectionInfo);
        } else { // if instance is expired
            $('#whale-panel-started').hide(); // hide the panel instance is up       
            $('#whale-panel-stopped').show(); // show the panel instance is down     
            $('#whale-challenge-lan-domain').html(''); 
        }
 
        
    });

    // get renaming mana for user
    CTFd.fetch("/api/v1/plugins/ctfd-chall-manager/mana", {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    }).then(function (response) {
        
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (response.success) response = response.data;
        else CTFd._functions.events.eventAlert({
            title: "Fail",
            html: response.data.message,
        });
        return response
    }).then(function (response){
        if (response.total == 0){
            $('.cm-panel-mana-cost-div').hide();  // hide the mana cost div if mana is disabled
        }
        else {
            let remaining = response.total - response.used
            $('#cm-challenge-mana-remaining').html(remaining);
        }
    });
};

CTFd._internal.challenge.destroy = function() {
    return new Promise((resolve, reject) => {
        var challenge_id = CTFd._internal.challenge.data.id;
        var url = "/api/v1/plugins/ctfd-chall-manager/instance"

        $('#whale-button-destroy').text("Waiting...");
        $('#whale-button-destroy').prop('disabled', true);

        let params = {
            "challengeId": challenge_id,
        };
    

        CTFd.fetch(url, {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(response => {
            if (response.status === 429 || response.status === 403) {
                return response.json();
            }
            return response.json();
        }).then(response => {
            if (response.success) {
                loadInfo();
                CTFd._functions.events.eventAlert({
                    title: "Success",
                    html: "Your instance has been destroyed!",
                });
                resolve();
            } else {
                CTFd._functions.events.eventAlert({
                    title: "Fail",
                    html: response.data.message,
                });
                reject(response.message);
            }
        }).catch(error => {
            reject(error);
        }).finally(() => {
            $('#whale-button-destroy').text("Destroy");
            $('#whale-button-destroy').prop('disabled', false);
        });
    });
};


CTFd._internal.challenge.renew = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-chall-manager/instance";

    $('#whale-button-renew').text("Waiting...");
    $('#whale-button-renew').prop('disabled', true);

    var params = {
        "challengeId": challenge_id,
    };

    CTFd.fetch(url, {
        method: 'PATCH',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (response.success) {
            loadInfo();
            CTFd._functions.events.eventAlert({
                title: "Success",
                html: response.data.message, // load custom message from api
            });
        } else {
            CTFd._functions.events.eventAlert({
                title: "Fail",
                html: response.data.message,
            });
        }
    }).finally(() => {
        $('#whale-button-renew').text("Renew");
        $('#whale-button-renew').prop('disabled', false);
    });
};

CTFd._internal.challenge.boot = function() {
    return new Promise((resolve, reject) => {
        var challenge_id = CTFd._internal.challenge.data.id;
        var url = "/api/v1/plugins/ctfd-chall-manager/instance";

        $('#whale-button-boot').text("Waiting...");
        $('#whale-button-boot').prop('disabled', true);

        var params = {
            "challengeId": challenge_id.toString()
        };

        CTFd.fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(response => {
            if (response.status === 429 || response.status === 403) {
                return response.json();
            }
            return response.json();
        }).then(response => {
            if (response.success) {
                loadInfo();
                CTFd._functions.events.eventAlert({
                    title: "Success",
                    html: "Your instance has been deployed!",
                });
                resolve();
            } else {
                CTFd._functions.events.eventAlert({
                    title: "Fail",
                    html: response.data.message,
                });
            }
        }).catch(error => {
            reject(error);
        }).finally(() => {
            $('#whale-button-boot').text("Launch an instance");
            $('#whale-button-boot').prop('disabled', false);
        });
    });
};


CTFd._internal.challenge.restart = function() {
    $('#whale-button-boot').prop('disabled', true);
    $('#whale-button-restart').prop('disabled', true);
    $('#whale-button-renew').prop('disabled', true);
    $('#whale-button-destroy').prop('disabled', true);
    
    // First, destroy the current challenge instance
    CTFd._internal.challenge.destroy().then(() => {
        // Then, boot a new challenge instance
        return CTFd._internal.challenge.boot();
    }).then(() => {
        // Finally, load the challenge info
        loadInfo();
        $('#whale-button-boot').prop('disabled', false);
        $('#whale-button-restart').prop('disabled', false);
        $('#whale-button-renew').prop('disabled', false);
        $('#whale-button-destroy').prop('disabled', false);
    }).catch((error) => {
        console.error('Error during restart:', error);
    });
    
}
