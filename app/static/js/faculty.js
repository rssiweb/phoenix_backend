Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Faculties',

        error: '',
        message: '',
        loading: 'Loading ...',

        faculties: [],
        facultyToReset: {},

        facultyToUpdate: {},
        isFacultyUpdate: false,
        confirmPassword: '',
        addingOrUpdating: false,

        searchTxt: '',
    },
    created: function(){
        this.loadv2([
            {name:'Faculties',
             url:'/api/admin/faculty/'+this.branchId+'/list',
             variableName: 'faculties',
             dataInReponse: 'faculties'},
             ])
    },
    updated: function(){
        $(this.$el).find('table').tablesort()
        $(this.$el).find('.dropdown').dropdown()
    },
    methods: {
        showResetDialog(faculty) {
            this.facultyToReset = faculty
            $('#resetModal').modal('show')
        },
        addFaculty() {
            var vm = this
            var loading = 'Adding ' + this.facultyToUpdate.name + '...'
            
            var postData = this.facultyToUpdate
            console.log('adding', postData)

            var url = '/api/admin/faculty/add'
            
            vm.$http.post(url,postData, vm.getHeaders())
            .then((response) => {
                console.log(response);
                if(response.body.status=='success'){
                    vm.faculties.push(response.body.faculty)
                    vm.resetFacultyForm()
                }else{
                    vm.error = response.body.message
                }
                vm.loading = ''
            },
            (error) => {
                console.log(error)
                vm.error = error.statusText
                vm.loading = ''
            });
        },
        updateFaculty() {
            if(!this.isFacultyUpdate){
                return this.addFaculty()
            }
            var vm = this
            var postData = this.facultyToUpdate
            var url = '/api/admin/faculty/update'
            var facultyIndex = this.getFacIndex(this.facultyToUpdate)

            vm.addingOrUpdating = true
            
            vm.$http.post(url,postData, vm.getHeaders())
            .then((response) => {
                console.log(response)
                vm.addingOrUpdating = false
                if(response.body.status == 'success'){
                    vm.resetFacultyForm()
                    vm.$set(vm.faculties, facultyIndex, response.body.faculty)
                }else{
                    vm.error = response.body.message
                }
            }, (error) => {
                vm.addingOrUpdating = false
                console.log(error);
                vm.error = error.statusText
            });
            
        },
        markFacultyToUpdate(faculty) {
            console.log('update', faculty)
            this.isFacultyUpdate = true
            this.facultyToUpdate = Object.assign({}, faculty)
            $('#addFacultyForm select').dropdown('set selected', this.facultyToUpdate.gender)
        },
        resetPassword() {
            console.log('reset password', this.facultyToReset)
            var vm = this
            var postData = this.facultyToReset
            var loading = 'Updating ' + this.facultyToReset.name + '\'s Password ...'
            var url = '/api/admin/faculty/reset'
            var facultyIndex = this.getFacIndex(this.facultyToReset)
            console.log(postData)
            vm.$http.post(url, postData, vm.getHeaders())
            .then((response) => {
                console.log(response)
                var toastConfig = {
                    theme: 'primary',
                    className: "ui olive label",
                    position: "bottom-right", 
                    icon : 'check',
                    duration : 3000
                }
                var msg = ''
                if(response.body.status == 'success') {
                    toastConfig.className = 'ui olive label'
                    vm.facultyToReset.password = ''
                    vm.facultyToReset.confirmPassword = ''
                } else {
                    toastConfig.className = 'ui orange label'
                }
                msg = response.body.message
                if(msg)
                    vm.$toasted.show(msg, toastConfig)
                vm.loading = ''
            }, (error) => {
                console.log(error)
                var toastConfig = {
                    theme: 'primary',
                    className: "ui orange label",
                    position: "bottom-right", 
                    icon : 'exclamation-triangle',
                    duration : 3000
                }
                var msg = error.body.message || error.statusText
                vm.$toasted.show(msg, toastConfig) 
            })
        },
        toogleActive(faculty) {
            faculty.stateLoading = true;
            var vm = this;
            vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            console.log(faculty)
            var url = '/api/admin/faculty/'+faculty.facultyId+'/active/'+(!faculty.active)
            
            vm.$http.put(url,{}, vm.getHeaders())
            .then((response) => {
                console.log(response);
                if(response.body.status=='success'){
                    console.log('done active')
                    faculty.active = !faculty.active;
                }else{
                    this.$toasted.show(response.body.message+' '+faculty.name + '\'s status did not change.',{ 
                        theme: 'primary',
                        className: "ui orange label",
                        position: "bottom-right", 
                        icon : 'exclamation-triangle',
                        duration : 3000
                    });    
                }
                faculty.stateLoading = false;
                vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            },
            (error) => {
                faculty.stateLoading = false;  
                console.log(error);
                this.$toasted.show(error.statusText + ' error occured. '+faculty.name + '\'s status did not change.',{ 
                    theme: 'primary',
                    className: "ui orange label",
                    position: "bottom-right", 
                    icon : 'exclamation-triangle',
                    duration : 3000
                });
                vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            });
        },
        toggleAdmin(faculty){
            faculty.adminLoading = true;
            var vm = this;
            vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            console.log(faculty)
            var url = '/api/admin/faculty/'+faculty.facultyId+'/admin/'+faculty.admin;
            console.log('WIP')
        },
        resetFacultyForm() {
            this.isFacultyUpdate = false
            this.facultyToUpdate = {}
            this.confirmPassword = ''
            $('#addFacultyForm select').dropdown('clear')
        },
        getJsonFromForm(formInputArr) {
            data = {}
            $(formInputArr).each(function(index, input){
                console.log(input)
                data[input.name] = input.value
                input.value = ''
            });
            return data
        },
        clearError(){
            this.error = ''
        },
        getFacIndex(fac) {
            var facultyIndex = -1
            this.faculties.forEach((fac, index) => {
                if (fac.facultyId == this.facultyToUpdate.facultyId) {
                    facultyIndex = index
                }
            })
            return facultyIndex
        },
        isValidPassword(password){
            if(!password){
                return {result:true}
            }
            res = {result: true, message:[]}
            if(password.length < 5){
                res.message.push('Must contain atleast 5 characters')
                res.result = false
            }
            if(password.search('[A-Z]') == -1){
                res.message.push('Must contain atleast one capital case character')
                res.result = false   
            }
            if(password.search('[a-z]') == -1){
                res.message.push('Must contain atleast one small case character')
                res.result = false
            }
            if (password.search('[0-9]') == -1){
                res.message.push('Must contain atleast one digit')
                res.result = false
            }
            return res
        }
    },
    computed:{
        matchPassword() {
            return !this.facultyToUpdate.password ||
            this.facultyToUpdate.password == this.confirmPassword;
        },
        facultyBtnTxt() {
            return this.isFacultyUpdate ?  "Update" : "Add";
        },
        enableFacultyBtn() {
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
               this.isValidPassword(this.facultyToUpdate.password).result &&
               this.isValidPassword(this.facultyToUpdate.password).message.length == 0 &&
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