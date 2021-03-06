#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Updated by Thonas Ball (2014)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import symbolic.z3_wrap as z3_wrap
from symbolic_types import SymbolicType, SymbolicExpression
import logging
import utils
from z3 import *

log = logging.getLogger("se.predicate")

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """
	def __init__(self, condexpr, result):
		self.expr = condexpr
		self.result = result
		self.sym_vars = {}
		svars = self.expr.getSymVariable()
		for name, var, sv in svars:
			self.sym_vars[name] = (var, sv)

	def __eq__(self, other):
		if isinstance(other, Predicate):
			res = self.result == other.result and self.expr.symbolicEq(other.expr)
			return res
		else:
			return False

	def __hash__(self):
		return hash(self.expr)

	def __str__(self):
		return str(self.expr) + " (was %s)" % (self.result)

	def __repr__(self):
		return repr(self.expr) + " (was %s)" % (self.result)

	def getSymVariable(self):
		return self.expr.getSymVariable()

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result

	def buildZ3Expr(self):
		if self.result == None:
			utils.crash("This predicate has an unknown result: %s" % self)

		sym_expr = self._buildZ3Expr()		
		if not is_bool(sym_expr):
			sym_expr = sym_expr != z3_wrap.int2BitVec(0, self.expr.getBitLength())
		if not self.result:
			sym_expr = Not(sym_expr)
		return (True, sym_expr)

	def _buildZ3Expr(self):
		if not (isinstance(self.expr,SymbolicType)):
			utils.crash("Unexpected expression %s" % self.expr)
		return z3_wrap.astToZ3Expr(self.expr, self.expr.getBitLength())