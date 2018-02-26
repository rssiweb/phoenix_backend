var app = new Vue({
    el: '#logincontainer',
    data: {
        error:'',
        loading: false,
    },
    methods:{
        getToken( event ) {
            event.preventDefault();
            this.loading=true;
            var postData = this.getJsonFromForm($('#loginForm input'))
            var vm = this;
            var url = '/api/get_token';

            vm.$http.post(url,postData)
            .then((response) => {
                console.log(response);
                console.log(response.body);
                var values = {expires: 1}
                Cookies.set('auth_token',response.body.auth_token, values);
                Cookies.set('is_admin',response.body.is_admin, values);
                this.loading = true;
                window.location = "/attendance";
            },
            (error) => {
                console.log(error);
                var message = 'Something bad happened';
                if(error.body)
                    message = error.body.message;
                else if (error.statusText)
                    message = error.statusText
                vm.error = message
                vm.loading = false
            });
        },
        showForgotDialog(){
            $('#forgotModal').modal('show');
        },
        getJsonFromForm: function(formInputArr){
            data = {}
            $(formInputArr).each(function(index, input){
                data[input.name] = input.value;
                input.value = '';
            });
            return data;
        },
    }
});
