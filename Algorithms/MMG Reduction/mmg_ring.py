from tulip import *
import numpy as np

class MMG_ring(object):
	"""
	This class specifies the arithmetic operators used to compute
	edge weights along the graph reduction.

	It also includes methods to recompute edge weights on the fly
	based on the computing history stored with each edge.
	"""
	def __init__(self):
		super(MMG_ring, self).__init__()

	def set_atomic_values(self, new_atomic_values):
		self.atomic_values = new_atomic_values

	def contract_operator(self, *weights):
		return sum(*weights)

	def merge_operator(self, *weights):
		return max(*weights)

	def _tokenize_(self, expression):
		if expression[0] in ['C', 'M']:
			count = 1
			token = expression[:2]
			i = 2
			while count > 0:
				if expression[i] == ')':
					count -= 1
					token += expression[i]
					i += 1
					continue
				elif expression[i] == '(':
					count += 1
					token += expression[i]
					i += 1
					continue
				else:
					token += expression[i]
					i += 1
					continue
		else:
			token = ''
			i = 0
			while i < len(expression) and expression[i] != ';':
				token += expression[i]
				i += 1
		if i == len(expression):
			return [token]
		else:
			out_token = [token] + [x for x in self._tokenize_(expression[i+1:])]
			return out_token

	def _evaluate_(self, expression):
		if expression[0] == 'M':
			return self.merge_operator(list(map(self._evaluate_, self._tokenize_(expression[2:-1]))))
		elif expression[0] == 'C':
			return self.contract_operator(list(map(self._evaluate_, self._tokenize_(expression[2:-1]))))
		else:
			return self.atomic_values[expression]


class MMG_plus_log(MMG_ring):
	def __init__(self):
		super(MMG_plus_log, self).__init__()

	def merge_operator(self, *weights):
		return sum([np.log(w) for w in list(*weights)])

	def contract_operator(self, *weights):
		return max(*weights)

class MMG_max_product(MMG_ring):
	def __init__(self):
		super(MMG_max_product, self).__init__()

	def merge_operator(self, *weights):
		return max(*weights)

	def contract_operator(self, *weights):
		return np.exp(sum([np.log(w) for w in list(*weights)]))
