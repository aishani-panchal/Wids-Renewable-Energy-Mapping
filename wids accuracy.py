#Add random column for train-test split
sampled = training.randomColumn('random', seed=42)

# Split data: 70% training, 30% testing
train_set = sampled.filter(ee.Filter.lt('random', 0.7))
test_set = sampled.filter(ee.Filter.gte('random', 0.7))

#Train classifier using training subset only
classifier = ee.Classifier.smileRandomForest(100).train(
    features=train_set,
    classProperty='class',
    inputProperties=feature_stack.bandNames()
)

#Classify test samples
validated = test_set.classify(classifier)

#Confusion matrix & accuracy metrics
confusion_matrix = validated.errorMatrix('class', 'classification')

print('Confusion Matrix:')
print(confusion_matrix.getInfo())

print('Overall Accuracy:')
print(confusion_matrix.accuracy().getInfo())

print('Kappa Coefficient:')
print(confusion_matrix.kappa().getInfo())

#Training accuracy 
train_confusion = classifier.confusionMatrix()

print('Training Confusion Matrix:')
print(train_confusion.getInfo())

print('Training Accuracy:')
print(train_confusion.accuracy().getInfo())

