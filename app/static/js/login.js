var showloading = function(){
    $('#login-btn').addClass('loading disabled');
    $('#error-message').addClass('hidden');
};
var hideLoading = function(){
    $('#login-btn').removeClass('loading disabled');
    $('#error-message').removeClass('hidden');
};
var saveToken = function(result){
        var values = {expires: 1}
        Cookies.set('auth_token',result.auth_token, values);
        window.location = "/attendance";
};
var errorgettingToken = function(result){
    $('#error-message').html(result.responseJSON.message);
    hideLoading();
}