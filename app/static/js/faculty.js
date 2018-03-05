var app = new Vue({
    el: '#app',
    data:{
        heading: 'Faculties',
        
        token: Cookies.get('auth_token'),
        is_admin: (Cookies.get('is_admin')=='true'),

        error:'',
        message:'',
        loading:'',

        faculties: [],
        facultyToReset: {},

        facultyToUpdate: {},
        confirmPassword: '',
    },
    created: function(){
        this.loadFaculties();
    },
    updated: function(){
        $(this.$el.getElementsByTagName('table')[0]).tablesort();
        $(this.$el.getElementsByTagName('select')).dropdown();
    },
    methods: {
        logout(){
            Cookies.remove('auth_token');
            window.location = '/';
        },
        getHeaders(){
            return {headers: { Authorization: 'Basic ' +  this.token}}
        },
        loadFaculties(){
            var url = '/api/admin/faculty';
            var vm = this;
            this.$http.get(url,this.getHeaders())
            .then((response) => {
                console.log(response);
                if(response.body.status=='success'){
                    vm.faculties = response.body.faculties;
                }else{
                    vm.message = response.body.message;
                }
                vm.loading = ''
            }, 
            (error) => {
                console.log(error);
                vm.loading = '';
                vm.error = error.body.message || error.statusText;
            });
        },
        resetPassword(faculty){
            console.log(faculty);
            this.facultyToReset = faculty;
            $('#resetModal').modal('show');
        },
        addFaculty(){
            var loading = 'Adding '+$('addFacultyForm input[name="name"]').val()+'...'
            var postData = this.facultyToUpdate
            console.log('updating', postData);
            var url = '/api/admin/faculty/add';
            var vm = this;
            vm.$http.post(url,postData, vm.getHeaders())
            .then((response) => {
                console.log(response);
                if(response.body.status=='success'){
                    vm.faculties.push(response.body.faculty)
                }else{
                    vm.error = response.body.message;
                }
                vm.loading = '';
            },
            (error) => {
                console.log(error);
                vm.error = error.statusText;
                vm.loading = '';
            });
        },
        getJsonFromForm(formInputArr){
            data = {}
            $(formInputArr).each(function(index, input){
                console.log(input)
                data[input.name] = input.value;
                input.value = '';
            });
            return data;
        },
    },
    computed:{
        matchPassword(){
            return !this.facultyToUpdate.password ||
            this.facultyToUpdate.password == this.confirmPassword;
        }
    },
    watch:{
        facultyToReset(){
            console.log('changed', this.facultyToReset)
        },
    },
    filters: {
      capitalize: function (value) {
        if (!value) return ''
            value = value.toString()
        return value.charAt(0).toUpperCase() + value.slice(1)
    }
}
});