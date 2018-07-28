var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        landed: false,
        loading: '',
        error: '',
        message: '',

        me: undefined,
        branches: [],
        exams: [],
        marks: {},
        subjects: [],
        students: [],
        categories: [],
        grades: [],
        faculties: [],

        selectedBranch: undefined,
        selectedExam: undefined,
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
        ], this.init)
    },
    updated: function(){
        $(this.$el).find('table.sortable').tablesort()
    },
    watch: {
        selectedBranch: function(){
            this.loadv2([{
                name:'Exams',
                url:'/api/exam/'+this.selectedBranch.id+'/list',
                variableName: 'exams',
                dataInReponse: 'exams'
            },
            {
                name:'Categories',
                url:'/api/category/'+this.selectedBranch.id+'/list',
                variableName: 'categories',
                dataInReponse: 'categories'
            },
            {
                name:'Grades',
                url:'/api/grade/'+this.selectedBranch.id+'/list',
                variableName: 'gradeRules',
                dataInReponse: 'grades'
            }
            ])
        },
        selectedExam: function(){
            this.loadv2([
            {
                name:'Students',
                url:'/api/student?ids=' + this.selectedExam.students,
                variableName: 'students',
                dataInReponse: 'students'
            },
            {
                name:'Subjects',
                url:'/api/subject/'+this.selectedBranch.id+'/list',
                variableName: 'subjects',
                dataInReponse: 'subjects'
            },
            {
                name:'Marks',
                url:'/api/admin/marks/exam/'+this.selectedExam.id,
                variableName: 'marks',
                dataInReponse: 'marks'
            }
            ], this.fixStudentCategory)
        }
    },
    computed: {
        catWiseStudents: function(){
            var cstds = {}
            this.students.forEach(std => {
                if (!cstds[std.category])
                    cstds[std.category] = []
                cstds[std.category].push(std)
            })
            return cstds
        },
    },
    methods: {
        init: function(){
            this.branches.forEach(branch => {
                if(branch.id === this.branchId)
                    this.branch = branch
            })
            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            dom.find('.ui.dropdown').dropdown()
            this.landed = true
        },
        onBranchChange: function(){
            var branchId = $('#branchDropDown').dropdown('get value')
            var branchId = parseInt(branchId)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === branchId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedBranch = this.branches[index]
            }
        },
        onExamChange: function(){
            var examId = $('#examDropDown').dropdown('get value')
            var examId = parseInt(examId)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === examId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedExam = this.exams[index]
            }
        },
        getMarks: function(std, sub){
            var testid = undefined
            this.selectedExam.tests.forEach(test => {
                if(test.subject===sub.id && test.category === std.category){
                    testid = test.id
                }
            })
            var marks = this.marks[testid]
            if(!marks){
                // console.log('No test for', sub.name, this.getCategoryName(std.category))
                return 'X'
            }
            var mark_value = undefined
            marks.forEach(mark=>{
                if(mark.student_id===std.id){
                    mark_value = mark.marks
                }
            })
            return mark_value || 'A'
        },
        getMaxMarks: function(sub, catId){
            var catId = parseInt(catId)
            console.log('getMaxMarks', sub, catId)
            var test = {max_marks: '-'}
            this.selectedExam.tests.forEach(t => {
                if(t.subject === sub.id && t.category === catId){
                    test = t
                }
            })
            return test.max_marks
        },
        fixStudentCategory: function(){
            console.log('called me', this.students)
            this.students.forEach((std, stdidx) => {
                this.selectedExam.tests.forEach(test => {
                    if (test.students.indexOf(std.id) != -1){
                        std.category = test.category
                        this.$set(std, this.students, stdidx)
                    }
                })
            })
        },
    }
})