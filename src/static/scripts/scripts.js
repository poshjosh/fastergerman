function Fastergerman() { }

const debug = true;

Fastergerman.prototype.toggleDisplay = function (elementId, flip = 'block', flop = 'none') {
  const element = document.getElementById(elementId);
  if (element.style.display !== flip) {
    element.style.display = flip;
  } else {
    element.style.display = flop;
  }
}

function isValidTime(time, errorElementId) {
  try {
    new Date(parseFloat(time));
    return true;
  } catch (e) {
    console.error("Invalid time: " + time + "\n" + e);
    // TODO - i18n
    document.getElementById(errorElementId).innerText = "Unexpected problem";
    return false;
  }
}

Fastergerman.prototype.startCountdown = function(endTime, formId, timeLeftElementId,
                                                 messageElementId, errorElementId) {
  if (debug) console.log("End time: " + endTime)
  if (endTime === "0" || endTime === 0) {
    return;
  }
  if (!isValidTime(endTime, errorElementId)) {
    return;
  }
  console.log("End date: " + Date(parseFloat(endTime)))

  const intervalId = setInterval(function(){
    // if (debug) console.log("Tick");
    const timeLeftElement = document.getElementById(timeLeftElementId);
    timeLeftElement.innerText = "" + (parseInt(timeLeftElement.innerText) - 1);
  }, 1000);

  const allowance = 1000; // 1 second before timeout
  const timeout = endTime - Date.now() - allowance;
  if (debug) console.log("Timeout: " + timeout);
  if (timeout <= allowance) {
    document.getElementById(formId).submit();
    return;
  }
  const countdownTimeoutId = setTimeout(function(){
    if (debug) console.log("Clearing interval");
    if (intervalId) {
      clearInterval(intervalId);
    }
    if (debug) console.log("Clearing countdown timeout");
    if (countdownTimeoutId) {
      clearTimeout(countdownTimeoutId);
    }
    document.getElementById(formId).submit();
  }, timeout);

  const messageTimeoutId = setTimeout(function() {
    if (debug) console.log("Clearing " + messageElementId + " timeout");
    if (messageTimeoutId) {
      clearTimeout(messageTimeoutId);
    }
    document.getElementById(messageElementId).innerHTML = "<p>&nbsp;</p>" // To keep the layout consistent
  }, 2000);
}

const fastergerman = new Fastergerman();
