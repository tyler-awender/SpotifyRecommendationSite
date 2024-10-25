const APIController = (function() {

    const clientId = 'f4968da54d444c79b4f9296ba647de85';
    const clientSecret = '755f3f594b074d1fb6a7cf8758fd0646';

    // private methods
    const _getToken = async () => {

        const result = await fetch('https://accounts.spotify.com/api/token', {
            method: 'POST',
            headers: {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'Basic ' + btoa( clientId + ':' + clientSecret)
            },
            body: 'grant_type=client_credentials'
        });

        const data = await result.json();
        return data.access_token;
    }

})();