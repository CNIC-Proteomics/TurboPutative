// Get string 00:00:00 indicating time of execution
execTime = function (initTime, currentTime) {
    
    // get current time in ms
    // let currentTime = new Date();
    // currentTime = currentTime.getTime();

    // get time difference in s
    let timeDiff = (currentTime - initTime)/1000;

    // get hours
    let hours = Math.floor(timeDiff/3600);
    hours = hours.toString().length == 1 ? `0${hours.toString()}` : hours.toString();

    // get minutes
    let minutes = Math.floor((timeDiff%3600)/60);
    minutes = minutes.toString().length == 1 ? `0${minutes.toString()}` : minutes.toString();

    // get seconds
    let seconds = Math.floor((timeDiff%3600)%60);
    seconds = seconds.toString().length == 1 ? `0${seconds.toString()}` : seconds.toString();

    // return time
    return (`${hours}:${minutes}:${seconds}`);
}

// Export module
module.exports = execTime;