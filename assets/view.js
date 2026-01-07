CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function () {
}

CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function () {
    loadInfo();
}

if (window.$ === undefined) window.$ = CTFd.lib.$;

const BOOT_DEFAULT_LABEL = "Launch the challenge";
const BOOT_STARTING_LABEL = "Starting...";
const STARTING_KEY_PREFIX = "cm-starting:";
const STARTING_TTL_MS = 10 * 60 * 1000;

function getStartingKey(challengeId) {
    return `${STARTING_KEY_PREFIX}${challengeId}`;
}

function markInstanceStarting(challengeId) {
    try {
        localStorage.setItem(
            getStartingKey(challengeId),
            JSON.stringify({ ts: Date.now() }),
        );
    } catch (e) {
        // storage unavailable, nothing to do
    }
}

function clearInstanceStarting(challengeId) {
    try {
        localStorage.removeItem(getStartingKey(challengeId));
    } catch (e) {
        // storage unavailable, nothing to do
    }
}

function isInstanceStarting(challengeId) {
    try {
        const raw = localStorage.getItem(getStartingKey(challengeId));
        if (!raw) return false;

        const parsed = JSON.parse(raw);
        if (!parsed.ts) return false;

        const age = Date.now() - parsed.ts;
        if (age > STARTING_TTL_MS) {
            clearInstanceStarting(challengeId);
            return false;
        }
        return true;
    } catch (e) {
        return false;
    }
}

function setBootButtonStarting() {
    $('#whale-button-boot').text(BOOT_STARTING_LABEL);
    $('#whale-button-boot').prop('disabled', true);
}

function resetBootButton() {
    $('#whale-button-boot').text(BOOT_DEFAULT_LABEL);
    $('#whale-button-boot').prop('disabled', false);
}

function renderStartingState() {
    $('#cm-panel-loading').hide();
    $('#cm-panel-until').hide();
    $('#whale-panel-started').hide();
    $('#whale-panel-stopped').show();
    $('#whale-challenge-lan-domain').html('');
    setBootButtonStarting();
}

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
    const pendingStart = isInstanceStarting(challenge_id);
    if (pendingStart) {
        setBootButtonStarting();
    } else {
        resetBootButton();
    }

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
        if (response.success) {
            response = response.data;
            clearInstanceStarting(challenge_id);
        } else {
            const code = response.data?.code || response.code;
            if (pendingStart && (code === 5 || code === 404 || code === 14)) {
                renderStartingState();
                return;
            }
            clearInstanceStarting(challenge_id);
            renderErrorAlert(response);
            return;
        }
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
                // expired but likely still being cleaned up server-side
                $('#whale-panel-started').show(); // show the panel instance is up
                $('#whale-panel-stopped').hide(); // hide the panel instance is down
                $('#whale-challenge-lan-domain').html(response.connectionInfo || '');
                $('#whale-challenge-count-down').text('terminating...');
                $('#cm-panel-until').show();
                // prevent booting a second instance while termination pending
                $('#whale-button-boot').prop('disabled', true).text('Terminating...');
            }
                    
        } else if (response.since) {    // if instance has no until
            $('#whale-panel-stopped').hide();
            $('#whale-panel-started').show();
            $('#whale-challenge-lan-domain').html(response.connectionInfo);
        } else { // if instance is expired
            $('#whale-panel-started').hide(); // hide the panel instance is up       
            $('#whale-panel-stopped').show(); // show the panel instance is down     
            $('#whale-challenge-lan-domain').html(''); 
            resetBootButton();
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
            html: response.message,
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
                    html: response.message,
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
                html: response.message,
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
        markInstanceStarting(challenge_id);
        setBootButtonStarting();

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
                clearInstanceStarting(challenge_id);
                resolve();
            } else {
            reject(error);
            }
        }).finally(() => {
            resetBootButton();
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


// // Old behavior in plugin for theme compatibility
// https://github.com/ctfer-io/ctfd-chall-manager/issues/234
CTFd._internal.challenge.submit = function(preview) {
    var challenge_id = parseInt($('#challenge-id').val())
    var submission = $('#challenge-input').val() // id changed in newer version of CTFd (old: #submission-input)

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview)
        params['preview'] = true

    return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};
