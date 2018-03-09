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
        isFacultyUpdate: false,
        confirmPassword: '',

        searchTxt: '',
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
        showResetDialog(faculty){
            this.facultyToReset = faculty;
            $('#resetModal').modal('show');
        },
        addFaculty(){
            var vm = this;
            var loading = 'Adding ' + this.facultyToUpdate.name + '...'
            
            var postData = this.facultyToUpdate
            console.log('adding', postData);

            var url = '/api/admin/faculty/add';
            
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
        updateFaculty(){
            if(!this.isFacultyUpdate){
                return this.addFaculty();
            }
            var vm = this;
            var postData = this.facultyToUpdate
            var loading = 'Updating ' + this.facultyToUpdate.name + '...'
            var url = '/api/admin/faculty/update';
            
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
        deleteFaculty(){
            console.log('deleteFaculty', this.facultyToUpdate);
            var vm = this;
            var postData = this.facultyToUpdate
            var loading = 'Deleting ' + this.facultyToUpdate.name + '...'
            var url = '/api/admin/faculty/delete';
            
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
        markFacultyToUpdate(faculty){
            console.log('update', faculty);
            this.isFacultyUpdate = true;
            this.facultyToUpdate = Object.assign({}, faculty);
            $('#addFacultyForm select').dropdown('set selected', this.facultyToUpdate.gender)
        },
        resetPassword(){
            console.log('reset password', this.facultyToReset);
            var vm = this;
            var postData = this.facultyToUpdate
            var loading = 'Updating ' + this.facultyToUpdate.name + '\'s Password ...'
            var url = '/api/admin/faculty/reset';
            
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
        resetFacultyForm(){
            this.isFacultyUpdate = false;
            this.facultyToUpdate = {};
            $('#addFacultyForm select').dropdown('clear'    )
        },
        getJsonFromForm(formInputArr){
            data = {}
            $(formInputArr).each(function(index, input){
                console.log(input)
                data[input.name] = input.value;
                input.value = '';
            });
            return data;
        }
    },
    computed:{
        matchPassword(){
            return !this.facultyToUpdate.password ||
            this.facultyToUpdate.password == this.confirmPassword;
        },
        facultyBtnTxt(){
            return this.isFacultyUpdate ?  "Update" : "Add";
        },
        enableFacultyBtn(){
            if(this.loading) return false;
            if(this.isFacultyUpdate &&
               this.facultyToUpdate.name &&
               this.facultyToUpdate.facultyId &&
               this.facultyToUpdate.email &&
               this.validEmail &&
               this.facultyToUpdate.gender)
                return true;
            if(!this.isFacultyUpdate &&
               this.facultyToUpdate.name &&
               this.facultyToUpdate.facultyId &&
               this.facultyToUpdate.email &&
               this.validEmail &&
               this.facultyToUpdate.gender &&
               this.facultyToUpdate.password == this.confirmPassword)
                return true;
            return false;
        },
        newPasswordMatch(){
            return this.facultyToReset.password==this.facultyToReset.confirmPassword;
        },
        filteredFaculties(){
            return this.faculties.filter(faculty => {
                if(this.lowerCaseSearchTxt == '')
                    return true;
                var name = this.lowerCaseSearchTxt.indexOf(faculty.name.toLowerCase()) != -1 || faculty.name.toLowerCase().indexOf(this.lowerCaseSearchTxt) != -1
                var id = this.lowerCaseSearchTxt.indexOf(faculty.facultyId) != -1 || faculty.facultyId.indexOf(this.lowerCaseSearchTxt) != -1
                var email = this.lowerCaseSearchTxt.indexOf(faculty.email) != -1 || faculty.email.indexOf(this.lowerCaseSearchTxt) != -1
                return name || id || email;
            });
        },
        lowerCaseSearchTxt(){
            return this.searchTxt.toLowerCase()
        },
        validEmail() {
            var email = this.facultyToUpdate.email
            if(!email) return true;
            var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
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