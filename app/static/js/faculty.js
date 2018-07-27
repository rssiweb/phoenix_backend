Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Faculties',

        error: '',
        resetError: '',
        facAddUpdateError: '',
        message: '',
        loading: 'Loading ...',

        branches: [],
        faculties: [],
        facultyToReset: {},

        facultyToUpdate: {},
        isFacultyUpdate: false,
        confirmPassword: '',
        addingOrUpdating: false,

        searchTxt: '',
        initModal: {},
        initFacultyForm: {
            on: 'blur',
            fields: {
                branch_id: 'empty',
                facultyId: 'empty',
                name: 'empty',
                gender: 'exactCount[1]',
                email: 'email',
            }
        },
        initResetForm: {
            on: 'blur',
            fields: {
                password: ['empty', 'minLength[6]'],
                confirmPassword: 'match[newpassword]',
            }
        },
        facModalInit: {
            onShow: function(){
                console.log('showing modal')
                var form = $('#addFacultyModal form')
                form.form(app.initFacultyForm)
                form.find('.dropdown').dropdown()
                form.form('clear')
                $(form).find('.ui.error.message').empty()

                if(app.isFacultyUpdate){
                    var values = app.facultyToUpdate
                    values.branch_id = app.facultyToUpdate.branch
                    form.form('set values', values)
                    form.form('remove rule', 'password', ['minLength[6]', 'empty'])
                    form.form('remove rule', 'confirmPassword', 'match[password]')
                }else{
                    form.form('add rule', 'password', ['minLength[6]', 'empty'])
                    form.form('add rule', 'confirmPassword', 'match[password]')
                }
            },
            onApprove: function(){
                
                app.facAddUpdateError = ''

                var form = $(this).find('form')
                form.find('.ui.error.message').empty()
                if(!form.form('is valid')){
                    form.form('validate form')
                } else {
                    app.loading = 'Adding faculty'
                    var data = form.form('get values')
                    app.addUpdateFaculty(data, function(){
                        $('#addFacultyModal').modal('hide')
                    })
                }
                return false
            }
        },
        resetPwdModalInit: {
            onShow: function(){
                console.log('showing modal')
                var form = $('#resetPasswordModal form')
                form.form(app.initResetForm)
                form.form('clear')
                form.find('.ui.error.message').empty()
            },
            onApprove: function(){
                
                app.resetError = ''

                var form = $(this).find('form')
                form.find('.ui.error.message').empty()

                if(!form.form('is valid')){
                    form.form('validate form')
                    return false
                }
                else{
                    app.loading = 'Updating password'
                    var data = form.form('get values')
                
                    app.resetPassword(data, function(){
                        $('#resetPasswordModal').modal('hide')
                    })
                    return false
                }
            }
        }
    },
    created: function(){
        this.loadv2([
        {
            name:'Faculties',
            url:'/api/admin/faculty/list',
            variableName: 'faculties',
            dataInReponse: 'faculties'
        },
        {
            name:'Branches',
            url:'/api/branch/list',
            variableName: 'branches',
            dataInReponse: 'branches'
        },
        ])
    },
    updated: function(){
        var dom = $(this.$el)
        dom.find('table').tablesort()
        dom.find('.dropdown').dropdown()
        dom.find('#addFacultyModal').modal(this.facModalInit)
        dom.find('#resetPasswordModal').modal(this.resetPwdModalInit)
    },
    methods: {
        showResetDialog(faculty) {
            this.facultyToReset = faculty
            this.showModal('resetPasswordModal')
        },
        showAddFaculty: function(){
            this.isFacultyUpdate = false
            this.showModal('addFacultyModal')
        },
        showUpdateFaculty: function(faculty){
            this.isFacultyUpdate = true
            this.facultyToUpdate = Object.assign({}, faculty)
            this.showModal('addFacultyModal')
        },
        addUpdateFaculty(postData, callback) {
            var vm = this

            var url = undefined
            if (this.isFacultyUpdate){
                url = '/api/admin/faculty/update'
                var loading = 'Updating ' + postData.name + '...'
            }
            else{
                url = '/api/admin/faculty/add'
                vm.loading = 'Adding ' + postData.name + '...'
            }
            
            vm.$http.post(url, postData)
            .then((response) => {
                console.log(response);
                if(response.body.status === 'success'){
                    
                    var newFaculty = response.body.faculty
                    if(vm.isFacultyUpdate){
                        // update the faculty to the list
                        var facIndex = vm.getFacIndex(newFaculty)
                        if(facIndex != -1)
                            vm.$set(vm.faculties, facIndex, response.body.faculty)
                        else {
                            vm.faculties.push(newFaculty)
                            console.log('Faculty updated but he is not present in the fac list')
                        }
                    } else {
                        // Add the faculty to the list
                        vm.faculties.push(newFaculty)
                    }

                    if(callback)
                        callback()
                    vm.showToast(response.body.message, 'success')
                } else {
                    vm.facAddUpdateError = response.body.message
                }
                vm.loading = undefined
            },
            (error) => {
                console.log(error)
                vm.showToast(error.body.message || error.statusText, 'warn')
                vm.loading = undefined
            });
        },
        markFacultyToUpdate(faculty) {
            console.log('update', faculty)
            this.isFacultyUpdate = true
            this.facultyToUpdate = Object.assign({}, faculty)
            $('#addFacultyForm select').dropdown('set selected', this.facultyToUpdate.gender)
        },
        updateFacultyBranch: function(event){
            this.facultyToUpdate.branch = event.target.value
            console.log('new branch value', event.target.value)
        },
        resetPassword(postData, callback) {
            console.log('reset password', postData)
            var vm = this
            var loading = 'Updating ' + postData.name + '\'s Password ...'
            var url = '/api/admin/faculty/reset'
            var facultyIndex = this.getFacIndex(this.facultyToReset)
            console.log(postData)
            vm.$http.post(url, postData)
            .then((response) => {
                console.log(response)
                if(response.body.status == 'success') {
                    if(callback)
                        callback()
                    vm.showToast(response.body.message, 'success')
                } else {
                    vm.resetError = response.body.message
                }
                vm.loading = undefined
            }, (error) => {
                console.log(error)
                vm.showToast(error.body.message || error.statusText, 'warn')
                vm.loading = undefined
            })
        },
        toogleActive(faculty) {
            faculty.stateLoading = true;
            var vm = this;
            vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            console.log(faculty)
            var url = '/api/admin/faculty/'+faculty.facultyId+'/active/'+(!faculty.active)
            
            vm.$http.put(url,{})
            .then((response) => {
                console.log(response);
                if(response.body.status === 'success'){
                    faculty.active = !faculty.active;
                }else{
                    vm.showToast(response.body.message+' '+faculty.name + '\'s status did not change.', 'error');
                }
                faculty.stateLoading = false;
                vm.$set(vm.faculties, vm.faculties.indexOf(faculty), faculty);
            },
            (error) => {
                faculty.stateLoading = false;  
                console.log(error);
                vm.showToast(error.statusText + ' error occured. '+faculty.name + '\'s status did not change.', 'error');
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
        getFacIndex(faculty) {
            var facultyIndex = -1
            this.faculties.forEach((fac, index) => {
                if (fac.facultyId == faculty.facultyId) {
                    facultyIndex = index
                }
            })
            return facultyIndex
        },
        isValidPassword(password){
            res = {result: true, message:[]}
            if(!password){
                return res
            }
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
        facultyBtnTxt() {
            return this.isFacultyUpdate ?  "Update" : "Add";
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
    },
    watch:{
    },
    filters: {
      capitalize: function (value) {
        if (!value) return ''
            value = value.toString()
        return value.charAt(0).toUpperCase() + value.slice(1)
    }
}
});