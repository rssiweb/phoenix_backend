var app = new Vue({
    el: '#app',
    data: {
        landed: false,
        token: Cookies.get('auth_token'),
        is_admin: (Cookies.get('is_admin')=='true'),
        me: {},
        currentPassword: '',
        password: '',
        confirmPassword: '',

    },
    created(){
        this.getProfile()
    },
    updated(){
        var dom = $(this.$el)
        dom.find('.dropdown').dropdown()
        dom.find('#afterLanding').show()
        this.landed = true
    },
    methods: {
        logout: function(){
            Cookies.remove('auth_token')
            window.location = '/'
        },
        getHeaders: function(){
            return {headers: { Authorization: 'Basic ' +  this.token}}
        },
        getProfile(){
            var vm = this
            this.$http.get('/api/myprofile',this.getHeaders())

            .then(response => {
                console.log(response)
                vm.me = response.body.me
            },
            error => {
                console.log(error)
            })
        },
        changePassword(){
            var vm = this
            var postData = {
                currentPassword: this.currentPassword,
                password: this.password
            }
            this.$http.post('/api/changepassword',postData ,this.getHeaders())
            .then(response => {
                console.log(response)    
            },
            error =>{
                console.log(error)
            })
        }
    },
    computed: {
        passwordErrors(){
            var password = this.password
            if(!password){
                return []
            }
            res = []
            if(password.length < 5){
                res.push('Must contain atleast 5 characters')
            }
            if(password.search('[A-Z]') == -1){
                res.push('Must contain atleast one capital case character')
            }
            if(password.search('[a-z]') == -1){
                res.push('Must contain atleast one small case character')
            }
            if (password.search('[0-9]') == -1){
                res.push('Must contain atleast one digit')
            }
            if (password.search('[!@#$%&*]') == -1){
                res.push("Must contain atleast one special character out of '!','@','#','$','%','&','*'")
            }
            return res
        }
    },
    watch: {}
})