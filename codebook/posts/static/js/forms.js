function QuestionContainer() {
    var self = this;
    self.questions = ko.observableArray([]);
    self.newQuestionTitle = ko.observable('');
    self.newQuestionContent = ko.observable('');
    self.newQuestionTags = ko.observableArray([]);
    self.newTags = ko.observableArray([]);
    self.newValue = ko.observable('');
    self.tagIds = {};
    self.tags = ko.observableArray([]);

    self.addQuestion = addQuestion;
    self.addTag = addTag;
    self.removeQuestion = removeQuestion;
    self.createTag = createTag;
    self.createNewTags = createNewTags;
    self.createQuestion = createQuestion;

    getTags();

    //----

    function addQuestion(authorId, append) {
        if (!self.newQuestionContent() || !self.newQuestionTitle()) {
            alert("Please add a title and some content");
            return;
        }
        self.createNewTags();
        self.createQuestion(authorId, append);
    }

    function createQuestion(authorId, append) {
        var data = {
            'author': authorId,
            'title': self.newQuestionTitle(),
            'content': self.newQuestionContent(),
            'tags': self.newQuestionTags(),
        }
        $.ajax(RESTAPI_URLS.QUESTIONS, {
            data: data,
            type: METHODS.POST
        }).done(function(data) {
            self.newQuestionTitle('');
            self.newQuestionContent('');
            if (append) {
                $.ajax({
                    url: RESTAPI_URLS.QUESTIONS + data['id'] + '/',
                    type: METHODS.GET
                }).done(function(data) {
                    self.questions.unshift(new QuestionListItemViewModel(data));
                });
            }
            self.newTags([]);
            self.newQuestionTags([]);
            alert("Success. You can see the new question in your profile.");
        });
    }

    function removeQuestion(question) {
        var conf = confirm("Are you sure you want to delete this question?");
        if (conf === true) {
            question.remove();
            self.questions.remove(question);
        }
    }

    function getTags() {
        $.ajax({
            url: RESTAPI_URLS.TAGS,
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(tag) {
                self.tagIds[tag['tag']] = tag['id'];
            });
            for(var k in self.tagIds) {
                self.tags.push(k);
            }
        });
    }

    function createNewTags() {
        self.newTags().forEach(function(tag){
            self.createTag(tag);
        });
    }

    function createTag(tag) {
        $.ajax({
            url: RESTAPI_URLS.TAGS,
            data: {
                tag: tag,
            },
            type: METHODS.POST
        }).done(function(data) {
            self.tagIds[tag] = data['id'];
            self.tags.push(tag);
            self.newQuestionTags.push(data['id']);
        });
    }

    function addTag() {
        if (!self.newValue()) {
            return;
        }
        if (!self.tagIds[self.newValue()]) {
            self.newTags.push(self.newValue());
        } else {
            self.newQuestionTags.push(self.tagIds[self.newValue()]);
        }
        self.newValue('');
    }

    return self;
}