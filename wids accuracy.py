# 1. Add random column for train-test split
sampled = training.randomColumn('random', seed=42)

# 2. Split data: 70% training, 30% testing
train_set = sampled.filter(ee.Filter.lt('random', 0.7))
test_set = sampled.filter(ee.Filter.gte('random', 0.7))

# 3. Train classifier using training subset only
classifier = ee.Classifier.smileRandomForest(100).train(
    features=train_set,
    classProperty='class',
    inputProperties=feature_stack.bandNames()
)

# 4. Classify validation (test) samples
validated = test_set.classify(classifier)

# 5. Confusion matrix & accuracy metrics
confusion_matrix = validated.errorMatrix('class', 'classification')

print('Confusion Matrix:')
print(confusion_matrix.getInfo())

print('Overall Accuracy:')
print(confusion_matrix.accuracy().getInfo())

print('Kappa Coefficient:')
print(confusion_matrix.kappa().getInfo())

# 6. (Optional) Training accuracy (resubstitution)
train_confusion = classifier.confusionMatrix()

print('Training Confusion Matrix:')
print(train_confusion.getInfo())

print('Training Accuracy:')
print(train_confusion.accuracy().getInfo())
