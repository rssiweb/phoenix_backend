var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        landed: false,

        examid: examid,

        faculties: [],
        branches: [],
        categories: [],
        subjects: [],
        tests: [],
        exam: {},
        catSubjects: [],
        
        cnfModal: {},

        testLoading: false,
        loading: 'Loading...',

        updateAction: false,

        error: '',
        message: '',

        initTestForm: {
            fields:{
                name: 'empty',
                testname: 'empty',
                maxMarks: ['number', 'empty'],
                category: 'empty',
                subject: 'empty',
                date: 'empty',
            }
        },
        initTestModal: {
            onShow: function(){
                var form = $(this).find('.form')
                form.form(app.initTestForm)
                form.find('.ui.error.message').empty()
                form.find('.ui.checkbox').checkbox()
            },
            onApprove: function(){
                var form = $(this).find('.form')
                $(form).find('.ui.error.message').empty()
                if(!form.form('is valid')){
                    form.form('validate form')
                    var data = form.form('get values')
                    console.log(data)
                    return false
                }
                var data = form.form('get values')
                if(app.updateAction){
                    app.updateTest(data)
                }else{
                    app.createTest(data)    
                }
                
            }
        },
        cnfModal: {
            heading: '',
            content: '',
            yes: 'Yes',
            no: 'No',
            action: '',
            data: {},
        },
        cnfModalInit: {
            onShow: function(){},
            onApprove: function(){
                if (app.cnfModal.action === 'DELETE_TEST'){
                    // data is test id in this case
                    app.deleteTest(app.cnfModal.data)
                }
                else if(app.cnfModal.action === 'DELETE_EXAM'){
                    app.deleteExam(app.cnfModal.data)
                }
            },
        },
    },
    created: function(){
        this.load(['branches', 'categories', 'subjects', 'faculties'], this.afterInit)
    },
    updated: function(){
        // initializing dropdowns and calendar here because when user
        // clicks on 'Add test' button the data changes which leads Vue to call updated
        $('.ui.dropdown').dropdown()
        $('.ui.calendar').calendar({type: 'date', minDate: new Date()})
        // $('#examModal .form').form(app.initExamForm)
    },
    computed:{

    },
    methods: {
        afterInit: function(){
            this.loadExam(examid)
        },
        showUi: function(){
            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            dom.find('#testModal').modal(this.initTestModal)
            dom.find('#cnfModal').modal(this.cnfModalInit)
            
            this.landed = true
        },
        getTest: function(testid){
            testid = parseInt(testid)
            var test = undefined
            this.tests.forEach((t, index)=>{
                if(t.id === testid)
                    test=t
            })
            return test
        },
        loadExam: function(id){
            var vm = this
            this.$http.get('/api/exam/'+id).
            then(response => {
                console.log(response)
                if(response.body.status==='success'){
                    vm.exam = response.body.exam
                    vm.tests = response.body.exam.tests
                    vm.exam.tests = undefined
                }else{
                    var msg = response.body.message || 'Cannot load exam!'
                    vm.showToast(msg,'warn','info')
                }
                vm.showUi()
            },
            error => {
                console.log(error)
                var msg = response.statusText
                vm.showToast(msg,'warn','info')
                vm.showUi()
            })
        },
        showCreateTest: function(){
            this.updateAction = false
            $('#testModal').find('.form').form('clear')
            $('#testModal').find('.form').find("input[name='name']").attr('disabled', false)
            this.showModal('testModal')
        },
        showUpdateTest: function(testid){
            var test = this.getTest(testid)
            if(!test)
                return
            this.updateAction = true
            var formValues = {}
            formValues.name = test.name
            formValues.subject = test.subject
            formValues.category = test.category
            formValues.id = test.id
            formValues.maxMarks = test.max_marks
            formValues.evaluator = test.evaluator
            formValues.date = moment(test.date,['DD/MM/YYYY']).format('MMM DD, YYYY')
            $('#testModal').find('.form').form('set values', formValues)
            $('#testModal .form #sub-dropdown').dropdown('set value',formValues.subject)
            $('#testModal .form #fac-dropdown').dropdown('set value',formValues.evaluator)
            $('#testModal').find('.form').find("input[name='name']").attr('disabled', true)
            $('#testModal').modal('show')
        },
        showDeleteTest: function(){
            var testid = $('#testModal').find('input[name="id"]').val()
            var test = this.getTest(testid)
            if(!test)
                return
            this.cnfModal.heading = 'Confirm Delete'
            this.cnfModal.content = 'Confirm delete test "'+test.name+'"?'
            this.cnfModal.action = 'DELETE_TEST'
            this.cnfModal.data = testid
            $('#cnfModal').modal('show')
        },
        categoryChanged: function(event){
            var catid = event.target.value
            this.catSubjects = this.getSubjects(catid)
            var dropdown = $('#sub-dropdown')
            var existingVal = dropdown.dropdown('get value')
            if (existingVal) existingVal = parseInt(existingVal)
                var valid = false
            console.log('existingVal', existingVal)
            this.catSubjects.forEach((sub, index)=>{
                console.log(sub)
                if(sub === existingVal){
                    valid = true
                }
            })
            if(!valid)
                dropdown.dropdown('clear')
        },
        getSubjects: function(catid){
            catid = parseInt(catid)
            var subjects = []
            var category = undefined
            this.categories.forEach((cat, index)=>{
                if(cat.id === catid){
                    category = cat
                }
            })
            if(!category)
                return subjects
            return category.subjects
        },
        getSubjectName: function(id){
            var name = ''
            this.subjects.forEach((sub, index)=>{
                if(sub.id === id){
                    name = sub.name
                }
            })
            return name
        },
        getSubjectNames: function(ids){
            var vm = this
            var names = ''
            if(!ids)
                return names
            ids.forEach((id, index)=>{
                var tmpName = vm.getSubjectName(id)
                if(tmpName){
                    names += tmpName + ', '
                }
            })
            if(names)
                return names.substring(0, names.length-2)
            return names
        },
        createTest: function(data){
            console.log(data)
            var vm = this
            data.date = moment(data.date,['MMM DD, YYYY']).format('DD/MM/YYYY')
            console.log(data)
            vm.testLoading = true
            this.$http.post('/api/admin/test/add', data).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var test = response.body.test
                    vm.tests.push(test)
                    vm.showToast('Successfully added ' + test.name, 'success', 'check')
                } else {
                    var msg = response.body.message || response.body.error || response.body.statusText || 'Cannot create test! Try again.'
                    vm.showToast(msg, 'warn', 'close')
                }
                vm.testLoading = false
            }, error => {
                console.log(error)
                var msg = error.statusText || 'Cannot create test! Try again.'
                vm.showToast(msg, 'warn', 'close')
                vm.testLoading = false
            })
        },
        updateTest: function(test){
            console.log(test)
            var vm = this
            vm.showToast('Updating '+test.name+'...','info', 'hourglass-o', true)
            test.date = moment(test.date,['MMM DD, YYYY']).format('DD/MM/YYYY')
            console.log(test)
            vm.testLoading = true
            this.$http.post('/api/admin/test/update/'+test.id, test).
            then(response => {
                console.log(response)
                vm.$toasted.clear()
                if(response.body.status === 'success'){
                    var test = response.body.test
                    var index = -1
                    vm.tests.forEach((t, i)=>{
                        if(t.id===test.id){
                            index = i
                        }
                    })
                    if(index != -1){
                        vm.$set(vm.tests, index, test)
                    }
                    vm.showToast('Successfully updated '+test.name, 'success', 'check')
                } else {
                    var msg = response.body.message || response.body.error || response.body.statusText || 'Cannot update test! Try again.'
                    vm.showToast(msg, 'warn', 'close')
                }
                vm.testLoading = false
            }, error => {
                console.log(error)
                var msg = error.statusText || 'Cannot update test! Try again.'
                vm.$toasted.clear()
                vm.showToast(msg, 'warn', 'close')
                vm.testLoading = false
            })
        },
        deleteTest: function(testid){
            var vm = this
            var test = vm.getTest(testid)
            console.log('delete test',test)
            vm.showToast('Deleting '+test.name+'...','info', 'hourglass-o', true)
            vm.$http.get('/api/admin/test/delete/'+testid)
            .then(response=>{
                console.log(response)
                vm.$toasted.clear()
                if (response.body.status==='success'){
                    var testid = response.body.id
                    var index = -1
                    vm.tests.forEach((t, i)=>{
                        if (testid === t.id)
                            index = i
                    })
                    if(index != -1){
                        vm.tests.splice(index, 1)
                    }
                    vm.showToast('Successfully deleted test','success', 'check')
                }
                else{
                    vm.showToast('Deleting test was unsuccessful','warn', 'close')
                }
            }
            ,error=>{
                console.log(error)
                vm.$toasted.clear()
                var msg = response.statusText || 'Unexpected error! Try again.'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        showDeleteExam: function(){
            this.cnfModal.heading = 'Confirm Delete'
            this.cnfModal.content = 'This exam contains ' + this.tests.length + ' Tests. Are you sure you want to delete this Exam?'
            this.cnfModal.action = 'DELETE_EXAM'
            $('#cnfModal').modal('show')
        },
        deleteExam: function(){
            console.log('delete exam', this.exam)
            var vm = this
            vm.$http.get('/api/admin/exam/delete/'+this.exam.id)
            .then(response => {
                console.log(response)
                if(response.body.status==='success'){
                    vm.showToast('Exam deleted, Redirecting to admin actions page...', 'success', 'check')
                    setTimeout(function(){
                        window.location = "/adminactions";
                    }, 2000)
                    
                } else {
                    var msg = response.body.statusMsg || response.body.error || response.body.message || 'Cannot delete exam! Try again.'
                    vm.showToast(msg, 'warn', 'close')
                }
            },
            error => {
                console.log(error)
                var msg = response.body.statusText || 'Unexpected error occured! Try again.'
                vm.showToast(msg, 'warn', 'close')
            })
        }
    },
});