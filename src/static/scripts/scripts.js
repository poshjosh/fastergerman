function Fastergerman() { /** Intentionally empty */ }

const production = false; // TODO - use environment
const debug = production === false;

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

Fastergerman.prototype.startCountdown = function(endTime, formId, countdownElementId,
                                                 messageElementId, errorElementId) {
  if (debug) console.log("End time: " + endTime);
  if (endTime === "0" || endTime === 0) {
    return;
  }
  if (!isValidTime(endTime, errorElementId)) {
    return;
  }
  console.log("End date: " + Date(parseFloat(endTime)))
  console.log("Countdown: " + document.getElementById(countdownElementId).innerText)

  const intervalId = setInterval(function(){
    const countdownElement = document.getElementById(countdownElementId);
    countdownElement.innerText = "" + (parseInt(countdownElement.innerText) - 1);
  }, 1000);

  const timeLeft = endTime - Date.now();
  if (debug) console.log("Time left: " + timeLeft);
  if (timeLeft <= 0) {
    document.getElementById(formId).submit();
    return;
  }
  const countdownTimeoutId = setTimeout(function(){
    if (debug) console.log("Clearing interval");
    if (intervalId) {
      clearInterval(intervalId);
    }
    if (debug) console.log("Clearing countdown");
    if (countdownTimeoutId) {
      clearTimeout(countdownTimeoutId);
    }
    document.getElementById(formId).submit();
  }, timeLeft);

  const messageTimeoutId = setTimeout(function() {
    if (debug) console.log("Clearing " + messageElementId);
    if (messageTimeoutId) {
      clearTimeout(messageTimeoutId);
    }
    document.getElementById(messageElementId).innerHTML = ""
  }, 2000);
}

const fastergerman = new Fastergerman();
