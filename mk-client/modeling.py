import numpy as np
import tensorflow as tf
from tqdm import tqdm
from scipy.stats import norm

def create_better_parameters(dataset, bounds, N=10):
    topKeys = list(reversed(sorted([(obj["ranking"], key) for key, obj in dataset.items()])))[:5]
    bestParams = [dataset[key]["parameters"] for ranking, key in topKeys]

    param_distribution = {}
    for param in bounds.keys():
        values = [params[param] for params in bestParams]
        mu, std = norm.fit(values)
        _min, _max = bounds[param]
        param_distribution[param] = {
            "mu": mu,
            "std": std,
            "min": _min,
            "max": _max
        }

    for n in tqdm(range(N)):
        parameters = {}
        for param, stats in param_distribution.items():
            parameters[param] = min(stats["max"], max(stats["min"], np.random.normal(stats["mu"], stats["std"])))
        yield parameters

def create_better_parameters(dataset, bounds):
    parameter_to_i = {k: i for i, k in enumerate(bounds.keys())}
    i_to_parameter = {i: param for param, i in parameter_to_i.items()}
    input_dims = len(parameter_to_i)
    hidden_dims = 1000

    # make the dataset
    X, Y = [], []
    for player_id, obj in dataset.items():
        vector = [0.0] * input_dims
        for param, value in obj["parameters"].items():
            vector[parameter_to_i[param]] = value
        X.append(vector)
        Y.append([obj["ranking"]])
    X, Y = map(np.array, [X, Y])
    Y = Y / 15.0 - 1.0

    # build the tf graph
    x = tf.placeholder(tf.float32, [len(dataset), input_dims])
    y_ = tf.placeholder(tf.float32, [len(dataset), 1])

    W = tf.Variable(tf.random_normal([input_dims, hidden_dims]))
    b = tf.Variable(tf.random_normal([hidden_dims]))
    h = tf.nn.elu(tf.matmul(x, W) + b)

    W = tf.Variable(tf.random_normal([hidden_dims, 1]))
    b = tf.Variable(tf.random_normal([1]))
    y = tf.matmul(h, W) + b

    loss = tf.reduce_sum(tf.pow(y_-y,2)) / len(dataset)
    train = tf.train.AdamOptimizer(0.001).minimize(loss)
    gradient = tf.gradients(loss, [x])

    sess = tf.InteractiveSession()
    tf.global_variables_initializer().run()

    # train
    for i in tqdm(range(10000)):
        sess.run(train, feed_dict={x: X, y_: Y})
        if i % 1000 == 0:
            print(sess.run(loss, feed_dict={x: X, y_: Y}))

    # compute gradients and update
    grad = sess.run(gradient, feed_dict={x: X, y_: Y})[0] / 10.0
    new_X = X + grad
    for vector, base_score in zip(new_X, Y):
        if base_score > np.mean(Y):
            parameters = {}
            for i, value in enumerate(vector):
                _min, _max = bounds[i_to_parameter[i]]
                parameters[i_to_parameter[i]] = min(_max, max(_min, value))
            yield parameters
