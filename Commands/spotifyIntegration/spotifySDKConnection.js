// Reference: https://developer.spotify.com/documentation/web-playback-sdk
const clientId = "CLIENT_ID";
const redirectUri = "http://127.0.0.1:8000/Commands/SpotifyIntegration/index.html";
const scopes = ["user-read-playback-state", "streaming"];

function authorise() {
  const url = `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(
      redirectUri
  )}&scope=${encodeURIComponent(scopes.join(" "))}&response_type=token`;
  location.href = url;
}

function getAccessToken() {
  const params = new URLSearchParams(window.location.hash.substring(1));
  const accessToken = params.get("access_token");
  return accessToken;
}

function initialisePlayer(token) {
  const player = new Spotify.Player({
    name: "Voice Assistant",
    getOAuthToken: (cb) => {
      cb(token);
    },
  });
  // Error handling
  player.addListener("initialization_error", ({message}) => {
    console.error(message);
  });
  player.addListener("authentication_error", ({message}) => {
    console.error(message);
  });
  player.addListener("account_error", ({message}) => {
    console.error(message);
  });
  player.addListener("playback_error", ({message}) => {
    console.error(message);
  });

  // If no errors occur
  player.addListener("ready", ({device_id}) => {
    console.log("Ready with Device ID", device_id);
  });

  // Connect to the player
  player.connect();
}

window.onSpotifyWebPlaybackSDKReady = () => {
  const accessToken = getAccessToken();
  if (accessToken) {
    initialisePlayer(accessToken);
  } else {
    authorise();
  }
};