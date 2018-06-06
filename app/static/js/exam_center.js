var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Exam Center',
        landed: false,

        students: [],
        branches: [],
        categories: [],
        exams: [],
        subjects: [],
        marks: [],
        tests: [],
        marks: [],
        result: {},
        gradeRules: [],
        branch: {},
        me: {},

        selectedTestId: -1,
        studentCatFilter: '',

        examLoading: false,
        marksLoading: false,
        deleteLoading: false,

        error: '',
        message: '',
        loading: 'Loading ...',
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
                if (app.cnfModal.action === 'DELETE_MARKS'){
                    // data is test id in this case
                    app.deleteMarks(app.cnfModal.data)
                }
            },
        },
    },
    created: function(){
        this.loadv2([
        {
            name:'Branches',
            url:'/api/branch/list',
            variableName: 'branches',
            dataInReponse: 'branches'
        },
        {
            name: 'Me',
            url: '/api/myprofile',
            variableName: 'me',
            dataInReponse: 'me'
        }
        ], this.after)
    },
    updated: function(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('#afterLanding').show()
        dom.find('.ui.dropdown').dropdown()
        this.landed = true
    },
    watch: {
        branch: function(){
            if(this.branch.id){
                this.examLoading = true
                this.loadv2([
                {
                    name:'Students',
                    url:'/api/student/'+this.branch.id+'/list',
                    variableName: 'students',
                    dataInReponse: 'students'
                },
                {
                    name:'Categories',
                    url:'/api/category/'+this.branch.id+'/list',
                    variableName: 'categories',
                    dataInReponse: 'categories'
                },
                {
                    name:'Exams',
                    url:'/api/exam/'+this.branch.id+'/list',
                    variableName: 'exams',
                    dataInReponse: 'exams'
                },
                {
                    name:'Subjects',
                    url:'/api/subject/'+this.branch.id+'/list',
                    variableName: 'subjects',
                    dataInReponse: 'subjects'
                },
                {
                    name:'Grades',
                    url:'/api/grade/'+this.branch.id+'/list',
                    variableName: 'gradeRules',
                    dataInReponse: 'grades'
                }
                ],this.afterExamLoaded)
            }
        },
        selectedTestId: function(){
            if(this.branch.id && this.selectedTestId){
                this.marksLoading = true
                this.loadv2([
                {
                    name:'Marks',
                    url:'/api/marks/'+this.selectedTestId,
                    variableName: 'marks',
                    dataInReponse: 'marks',
                    default: []
                },], this.afterMarksLoad)
            }
        }
    },
    computed: {
        filteredStudents: function(){
            return this.students.filter((std) => {
                return std.category === this.studentCatFilter
            })
        },
        selectedTest: function(){
            var test = undefined
            this.tests.forEach(t => {
                if(t.id === this.selectedTestId)
                    test = t
            })
            return test
        }
    },
    methods: {
        after: function(){
            this.heading = 'Exam Center'
            this.branches.forEach(branch=>{
                if(branch.id===this.branchId)
                    this.branch = branch
            })
            var dom = $(this.$el)
            dom.find('#cnfModal').modal(this.cnfModalInit)
        },
        afterExamLoaded: function(){
            this.examLoading = false
        },
        afterMarksLoad: function(){
            this.marksLoading = false
            this.marks.forEach(mark=>{
                var data  = {marks: mark.marks, comments: mark.comments, marksSaving: false, commentSaving:false}
                this.$set(this.result, mark.student_id, data)
            })
        },
        onBranchChange: function(){
            var data = $('#testForm').form('get values')
            var selectedBranchId = parseInt(data.branch)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === selectedBranchId){
                    index = i
                }
            })
            if(index != -1){
                this.branch = this.branches[index]
            }
        },
        onExamChange: function(){
            var data = $('#testForm').form('get values')
            var selectedExamId = parseInt(data.exam)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === selectedExamId){
                    index = i
                }
            })
            if(index != -1){
                $('#testDropdown').dropdown('clear')
                this.tests = []
                this.result = {}
                this.studentCatFilter = ''
                var allTests = this.exams[index].tests
                this.tests = allTests.filter(test => {
                    return this.me.admin || test.evaluator === this.me.id
                })
            }
        },
        onTestChange: function(){
            var data = $('#testForm').form('get values')
            if(!data.test) {
                return
            }
            this.selectedTestId = parseInt(data.test)
            var test = undefined
            this.tests.forEach((t, i)=>{
                if(t.id === this.selectedTestId){
                    test = t
                }
            })
            if(!test){
                return
            }
            this.studentCatFilter = test.category
            this.result = {}
        },
        setObtainedMarks: function(std_id, event){
            var vm = this
            console.log('setObtainedMarks', std_id, event.target.value)
            var data = this.result[std_id]
            if(!data){
                data = {}
            }
            var marks = event.target.value
            if(marks > this.selectedTest.max_marks){
                vm.highlightRowFor(std_id, 'negative')
                var data = this.result[std_id]
                if(!data){
                    return
                }
                var marks = data.marks || ''
                // reset the value to original value after a delay
                setTimeout(function(){
                    $('table tr[data-id="'+std_id+'"] input[name="marks"]').val(marks)
                }, 200)
                return
            }

            data['marks'] = marks
            data['marksSaving'] = true

            var grade = this.gradeFor(this.percentOf(event.target.value))
            data['comment'] = grade.comment
            data['commentSaving'] = true

            this.$set(this.result, std_id, data)
            var url = '/api/marks/set/' + this.selectedTest.id + '/' + std_id
            this.$http.post(url, data)
            .then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var data = response.body.marks
                    data.marksSaving = false
                    data.commentSaving = false
                    vm.$set(vm.result, std_id, data)
                    vm.highlightRowFor(data.student_id, 'positive')
                }
                else{
                    // required to update the loading state in UI
                    var data = vm.result[std_id]
                    data.marksSaving = false
                    data.commentSaving = false
                    vm.$set(vm.result, std_id, data)
                    vm.highlightRowFor(data.student_id, 'negative')
                }
            },
            error => {
                console.log(error)
                // required to update the loading state in UI
                var data = vm.result[std_id]
                data.marksSaving = false
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
                vm.highlightRowFor(data.student_id, 'negative')
            })
        },
        setComments: function(std_id, event){
            var vm = this
            console.log('setComments', std_id, event.target.value)
            var data = this.result[std_id] || {}
            data['comment'] = event.target.value
            data['commentSaving'] = true

            this.$set(this.result, std_id, data)
            var url = '/api/marks/set/' + this.selectedTest.id + '/' + std_id
            this.$http.post(url, data)
            .then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var data = response.body.marks
                    data.commentSaving = false
                    vm.$set(vm.result, std_id, data)
                    vm.highlightRowFor(data.student_id, 'positive')
                }
                else{
                    // required to update the loading state in UI
                    var data = vm.result[std_id]
                    data.marksSaving = false
                    data.commentSaving = false
                    vm.$set(vm.result, std_id, data)
                    vm.highlightRowFor(data.student_id, 'negative')
                }
            },
            error => {
                console.log(error)
                // required to update the loading state in UI
                var data = vm.result[std_id]
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
                vm.highlightRowFor(data.student_id, 'negative')
            })
        },
        gradeFor: function(percent){
            percent = Math.round(percent)
            var grade = {}
            this.gradeRules.forEach(gRule=>{
                if(gRule.min <= percent && gRule.max >= percent)
                    grade = gRule
            })
            return grade
        },
        getGrade: function(id){
            var percent = this.getPercentage(id)
            return this.gradeFor(percent)
        },
        percentOf: function(mo){
            var mo = parseInt(mo)
            var mm = this.selectedTest.max_marks
            if(mm)
                mm = parseInt(mm) || 0
            var percentage = 0
            if (mm > 0)
                percentage = (mo / mm * 100).toFixed(2)
            return percentage
        },
        getPercentage: function(id){
            var data = this.result[id]
            if(!data)
                return undefined
            var mo = data.marks
            if(!mo)
                return undefined
            return this.percentOf(mo)
        },
        getComments: function(id){
            // intentially leaving for undefined
            var data = this.result[id]
            if(data)
                return data.comments
        },
        getMarks: function(id){
          var data = this.result[id]
          if(data)
            return data.marks
    },
    showDeleteMarks: function(){
        var test = this.selectedTest
        if(!test)
            return
        this.cnfModal.heading = 'Confirm Delete'
        this.cnfModal.content = 'Are you sure you want to delete ALL marks for "'+this.selectedTest.name+'"? you won\'t be able to undo this.'
        this.cnfModal.action = 'DELETE_MARKS'
        this.cnfModal.data = test
        this.showModal('cnfModal')
    },
    deleteMarks: function(test){
        var vm = this
        console.log('I will delete ALL marks of ',test.name)
        this.deleteLoading = true
        this.$http.get('/api/marks/delete/' + test.id)
        .then(response=>{
            console.log(response)
            if(response.body.status === 'success'){
                vm.result = {}
                var msg = response.body.message || 'Successfuly deleted marks.'
                vm.showToast(msg, 'success', 'check')
            }else{
                var msg = response.body.message || 'Something unexpected happened, try again!'
                vm.showToast(msg, 'warn', 'info')
            }
            this.deleteLoading = false
        },
        error => {
            console.log(error)
            var msg = 'Something unexpected happened, try again!' || error.statusText 
            vm.showToast(msg, 'warn', 'info')
            this.deleteLoading = false
        })
    },
    highlightRowFor: function(dataid, color, secs){
        secs = parseInt(secs) || 1000
        $('table tr[data-id="' + dataid + '"]').addClass(color)
        setTimeout(function(){
            $('table tr[data-id="' + dataid + '"]').removeClass(color)
        }, secs)
    }
}
})