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
    const seconds = Math.floor((countdown / 1000) % 60);
    const minutes = Math.floor((countdown / (1000 * 60)) % 60);
    const hours = Math.floor((countdown / (1000 * 60 * 60)) % 24);
    const days = Math.floor((countdown / (1000 * 60 * 60 * 24 )) % 365);
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
    formattedCountdown = formattedCountdown + seconds.toString().padStart(2, '0') + "s";
    return formattedCountdown;
}

function handleResponse(response) {
    if (response.status === 429 || response.status === 403) {
        // User was ratelimited or not logged in or CTF is paused.
        return response.json();
    }
    return response.json();
}


function loadInfo() {
    const challenge_id = CTFd._internal.challenge.data.id;
    const mana_cost = CTFd._internal.challenge.data.mana_cost;
    const instanceUrl = "/api/v1/plugins/ctfd-chall-manager/instance?challengeId=" + challenge_id;
    const manaUrl = "/api/v1/plugins/ctfd-chall-manager/mana"
    const cacheKey = "CTFd:ctfd-chall-manager:instance_" + challenge_id
    const cacheValidity = 30000 // 30s

    const getDataFromLocalStorage = () => {
        const dataStringified = localStorage.getItem(cacheKey);
        return JSON.parse(dataStringified) || null;
    }

    const isValidCache = (instanceData) => {
        var valid = false
        if (instanceData && instanceData.receivedAt) {
            valid = new Date() - new Date(instanceData.receivedAt) < cacheValidity
            if (!valid) {
                localStorage.removeItem(cacheKey)
            }
        }
        return valid
    }
    const instanceData = getDataFromLocalStorage();

    // Fetch instance and mana data in parallel
    // Fetch instance info only if there are nothing in localStorage
    const fetchInstance = isValidCache(instanceData) ? Promise.resolve(instanceData.response) : CTFd.fetch(instanceUrl, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    }).then(handleResponse).then((instanceResponse) => {
         // Handle instance response
        if (instanceResponse.success) {
            instanceResponse = instanceResponse.data;
        } else {
            CTFd._functions.events.eventAlert({
                title: "Fail",
                html: instanceResponse.message,
            });
        }
        return instanceResponse
    }).then((instanceResponse) => {
        // If instance exists (since is not null) then store in cache
        if (instanceResponse.since) {
            localStorage.setItem(cacheKey, JSON.stringify({response: instanceResponse, receivedAt: new Date()}));
        }
        return instanceResponse
    })

    // Fetch mana information for the user only if the challenge defines mana_cost
    // And only if the instance is not running
    const fetchMana = mana_cost != 0 && !isValidCache(instanceData) ? CTFd.fetch(manaUrl, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    }).then(handleResponse) : Promise.resolve(null);

    Promise.all([fetchInstance, fetchMana]).then(([instanceResponse, manaResponse]) => {
        if (window.t !== undefined) {
            clearInterval(window.t);
            window.t = undefined;
        }

        // Default UI
        $('#cm-panel-loading').hide();
        $('#cm-panel-until').hide();
        $('#whale-panel-stopped').show();
        $('#whale-panel-started').hide();
        $('#whale-challenge-lan-domain').html('');

        // if instance is running
        if (instanceResponse.since) {
            $('#whale-panel-stopped').hide();
            $('#whale-panel-started').show();
        }

        // prevent error if instance has no connectionInfo
        // https://github.com/ctfer-io/ctfd-chall-manager/issues/132
        if (instanceResponse.connectionInfo) {
            $('#whale-challenge-lan-domain').html(instanceResponse.connectionInfo);
            
        }

        if (instanceResponse.until) {
            $('#cm-panel-until').show();
            var now = new Date();
            var until = new Date(instanceResponse.until);
           //  console.log(until);
            var count_down = until - now;
            if (count_down > 0) {                
                $('#whale-challenge-count-down').text(formatCountDown(count_down));
                window.t = setInterval(() => {
                    count_down = until - new Date();
                    if (count_down <= 0) {
                        loadInfo();
                    }
                    $('#whale-challenge-count-down').text(formatCountDown(count_down));
                }, 1000);
            } else {
                // do not hide the connectionInfo 
                // https://github.com/ctfer-io/ctfd-chall-manager/issues/231
                $('#whale-challenge-count-down').html('Terminating...');
            }
        } 

        // Handle mana response if it exists
        if (manaResponse) {
            if (manaResponse.success) {
                manaResponse = manaResponse.data;
            } else {
                CTFd._functions.events.eventAlert({
                    title: "Fail",
                    html: manaResponse.message,
                });
            }

            if (manaResponse.total == 0) {
                $('.cm-panel-mana-cost-div').hide();
            } else {
                let remaining = manaResponse.total - manaResponse.used;
                $('#cm-challenge-mana-remaining').html(remaining);
            }
        }
    }).catch(error => {
        console.error('Error loading info:', error);
    });
}


CTFd._internal.challenge.destroy = function() {
    return new Promise((resolve, reject) => {
        const challenge_id = CTFd._internal.challenge.data.id;
        const url = "/api/v1/plugins/ctfd-chall-manager/instance"
        const cacheKey = "CTFd:ctfd-chall-manager:instance_" + challenge_id

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
        }).then(handleResponse).then(response => {
            if (response.success) {
                localStorage.removeItem(cacheKey) // clear the cache to retrigger its sync while loadInfo
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
    const challenge_id = CTFd._internal.challenge.data.id;
    const url = "/api/v1/plugins/ctfd-chall-manager/instance";
    const cacheKey = "CTFd:ctfd-chall-manager:instance_" + challenge_id

    $('#whale-button-renew').text("Waiting...");
    $('#whale-button-renew').prop('disabled', true);

    const params = {
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
    }).then(handleResponse).then(function (response) {
        if (response.success) {
            localStorage.removeItem(cacheKey) // clear the cache to retrigger its sync while loadInfo
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
        }).then(handleResponse).then(response => {
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
                    html: response.message,
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